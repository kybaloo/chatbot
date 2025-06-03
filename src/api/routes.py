"""
Routes FastAPI pour l'API REST
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from ..services.conversation_service import ConversationService
from ..services.ai_service import AIService
from ..utils.logger import log_error


# Modèles Pydantic pour l'API
class ChatRequest(BaseModel):
    """Modèle pour une requête de chat"""

    question: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Modèle pour une réponse de chat"""

    id: str
    question: str
    answer: str
    conversation_id: Optional[str] = None


class ConversationSummary(BaseModel):
    """Résumé d'une conversation pour les listes"""

    conversation_id: str
    created_at: str
    updated_at: str
    message_count: int
    title: Optional[str] = None


class ConversationDetail(BaseModel):
    """Détail complet d'une conversation"""

    conversation_id: str
    user_id: str
    username: Optional[str] = None
    created_at: str
    updated_at: str
    messages: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


# Dépendances pour l'injection
def get_conversation_service():
    """Retourne une instance de ConversationService"""
    return ConversationService()


def get_ai_service():
    """Retourne une instance de AIService"""
    return AIService()


# Création du router
router = APIRouter(tags=["Chat"])


@router.get("/")
async def root():
    """Endpoint racine pour vérifier que l'API fonctionne"""
    return {"status": "ok", "message": "Hello World"}


@router.get("/health")
async def health_check(
    conversation_service: ConversationService = Depends(get_conversation_service),
    ai_service: AIService = Depends(get_ai_service),
):
    """Endpoint pour vérifier l'état des services"""
    return {
        "status": "ok",
        "services": {
            "api": "available",
            "ai_service": "available",  # On assume qu'il est disponible s'il n'y a pas d'erreur
            "storage": "available" if conversation_service.is_storage_available() else "unavailable"
        },
        "message": "Chat is available" + (" (conversations will not be saved)" if not conversation_service.is_storage_available() else "")
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Endpoint pour discuter avec le bot
    Si user_id et conversation_id sont fournis, la conversation sera sauvegardée (si possible)
    Le chat fonctionne même si la sauvegarde échoue
    """
    try:
        # Récupérer ou créer une conversation si user_id est fourni
        conversation = None
        storage_failed = False
        
        if request.user_id:
            if request.conversation_id:
                conversation = await conversation_service.get_by_user_and_conversation(
                    request.user_id, request.conversation_id
                )

            if not conversation:
                if conversation_service.is_storage_available():
                    # Essayer de créer une conversation persistante
                    conversation = await conversation_service.create_new_conversation(
                        request.user_id
                    )
                    # Vérifier si la création a vraiment réussi
                    if conversation and conversation.conversation_id:
                        request.conversation_id = conversation.conversation_id
                    else:
                        storage_failed = True
                else:
                    storage_failed = True
                
                # Si le stockage a échoué, créer une conversation temporaire
                if storage_failed:
                    conversation = conversation_service.create_temporary_conversation(
                        request.user_id
                    )
                    request.conversation_id = conversation.conversation_id

            # Ajouter le message utilisateur à la conversation
            conversation.add_message(role="user", content=request.question)

        # Préparer les messages pour l'API Mistral
        messages = []
        if conversation and conversation.messages:
            messages = conversation.get_messages_for_ai()
        else:
            messages = [{"role": "user", "content": request.question}]

        # Appeler l'API Mistral
        chat_response = await ai_service.chat_completion(messages)

        # Extraire la réponse
        assistant_response = chat_response["content"]

        # Si une conversation est en cours, ajouter la réponse et tenter de sauvegarder
        if conversation:
            conversation.add_message(role="assistant", content=assistant_response)
            
            # Essayer de sauvegarder seulement si le stockage est disponible
            if conversation_service.is_storage_available() and not storage_failed:
                try:
                    await conversation_service.update(
                        conversation.conversation_id, conversation
                    )
                except Exception as e:
                    # Log l'erreur mais continue le traitement
                    log_error(f"Failed to save conversation: {str(e)}", exc_info=True)
                    storage_failed = True

        # Retourner la réponse
        result = ChatResponse(
            id=chat_response["id"],
            question=request.question,
            answer=assistant_response,
            conversation_id=request.conversation_id,
        )

        return result

    except Exception as e:
        # Log l'erreur mais essaie de fournir une réponse utile
        log_error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        
        # Si c'est une erreur liée au stockage mais que l'IA fonctionne, 
        # on peut essayer de continuer sans sauvegarde
        if "credentials" in str(e).lower() or "dynamodb" in str(e).lower():
            try:
                # Essayer de répondre sans sauvegarde
                messages = [{"role": "user", "content": request.question}]
                chat_response = await ai_service.chat_completion(messages)
                
                return ChatResponse(
                    id=chat_response["id"],
                    question=request.question,
                    answer=chat_response["content"],
                    conversation_id=None,  # Pas de conversation sauvegardée
                )
            except Exception as ai_error:
                log_error(f"AI service also failed: {str(ai_error)}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail="Both storage and AI services are unavailable"
                )
        
        # Pour les autres types d'erreurs, retourner l'erreur
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{user_id}", response_model=List[ConversationSummary])
async def get_user_conversations(
    user_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Récupère toutes les conversations d'un utilisateur"""
    try:
        # Vérifier si le stockage est disponible
        if not conversation_service.is_storage_available():
            # Retourner une liste vide si pas de stockage
            return []
            
        conversations = await conversation_service.get_by_user(user_id)

        # Convertir les conversations en format pour l'API
        result = []
        for conv in conversations:
            # Trouver un titre pour la conversation dans les métadonnées ou utiliser le premier message
            title = conv.metadata.get("title") if conv.metadata else None
            if not title and conv.messages:
                for msg in conv.messages:
                    if msg.role == "user":
                        title = (
                            msg.content[:50] + "..."
                            if len(msg.content) > 50
                            else msg.content
                        )
                        break

            result.append(
                ConversationSummary(
                    conversation_id=conv.conversation_id,
                    created_at=conv.created_at.isoformat(),
                    updated_at=conv.updated_at.isoformat(),
                    message_count=len(conv.messages),
                    title=title,
                )
            )

        return result

    except Exception as e:
        log_error(f"Error getting conversations for user {user_id}: {str(e)}")
        # Si c'est une erreur de stockage, retourner une liste vide plutôt qu'une erreur
        if "credentials" in str(e).lower() or "dynamodb" in str(e).lower():
            return []
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/conversations/{user_id}/{conversation_id}", response_model=ConversationDetail
)
async def get_conversation(
    user_id: str,
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Récupère une conversation spécifique"""
    try:
        # Vérifier si le stockage est disponible
        if not conversation_service.is_storage_available():
            raise HTTPException(
                status_code=503, 
                detail="Storage service unavailable. Conversations are not persisted."
            )
            
        conversation = await conversation_service.get_by_user_and_conversation(
            user_id, conversation_id
        )

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Convertir les messages en format pour l'API
        messages = []
        for msg in conversation.messages:
            messages.append(
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
            )

        return ConversationDetail(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            username=conversation.username,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            messages=messages,
            metadata=conversation.metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error getting conversation {conversation_id}: {str(e)}")
        # Si c'est une erreur de stockage, retourner une erreur de service non disponible
        if "credentials" in str(e).lower() or "dynamodb" in str(e).lower():
            raise HTTPException(
                status_code=503, 
                detail="Storage service unavailable. Conversations are not persisted."
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{user_id}/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Supprime une conversation"""
    try:
        # Vérifier si le stockage est disponible
        if not conversation_service.is_storage_available():
            raise HTTPException(
                status_code=503, 
                detail="Storage service unavailable. Cannot delete conversations."
            )
            
        result = await conversation_service.delete_by_user_and_conversation(
            user_id, conversation_id
        )
        if not result:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {"status": "ok", "message": "Conversation deleted"}

    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error deleting conversation {conversation_id}: {str(e)}")
        # Si c'est une erreur de stockage, retourner une erreur de service non disponible
        if "credentials" in str(e).lower() or "dynamodb" in str(e).lower():
            raise HTTPException(
                status_code=503, 
                detail="Storage service unavailable. Cannot delete conversations."
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/conversations/{user_id}/{conversation_id}")
async def update_conversation(
    user_id: str,
    conversation_id: str,
    title: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """Met à jour les métadonnées d'une conversation (titre)"""
    try:
        # Vérifier si le stockage est disponible
        if not conversation_service.is_storage_available():
            raise HTTPException(
                status_code=503, 
                detail="Storage service unavailable. Cannot update conversations."
            )
            
        conversation = await conversation_service.rename_conversation(
            user_id, conversation_id, title
        )

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {"status": "ok", "message": "Conversation updated"}

    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error updating conversation {conversation_id}: {str(e)}")
        # Si c'est une erreur de stockage, retourner une erreur de service non disponible
        if "credentials" in str(e).lower() or "dynamodb" in str(e).lower():
            raise HTTPException(
                status_code=503, 
                detail="Storage service unavailable. Cannot update conversations."
            )
        raise HTTPException(status_code=500, detail=str(e))
