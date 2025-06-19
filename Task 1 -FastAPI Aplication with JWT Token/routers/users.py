from fastapi import APIRouter, Depends, HTTPException
from conv_ret_db import SessionLocal, ConversationChatHistory, UserRegistry
from dependencies import verify_token
from schemas import Conversation, ConversationList

router = APIRouter()

@router.get("/profile")
async def get_user_profile(auth_data: dict = Depends(verify_token)):
    session = SessionLocal()
    try:
        user = session.query(UserRegistry).filter_by(id=auth_data["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "username": user.username,
            "email": user.email,
            "current_session_id": auth_data["chatbot_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")
    finally:
        session.close()

@router.get("/conversations", response_model=ConversationList)
async def get_user_conversations(
    auth_data: dict = Depends(verify_token),
    limit: int = 10,
    offset: int = 0
):
    chatbot_id = auth_data["chatbot_id"]
    session = SessionLocal()
    try:
        conversations = session.query(ConversationChatHistory)\
            .filter_by(chatbot_id=chatbot_id)\
            .order_by(ConversationChatHistory.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        total_conversations = session.query(ConversationChatHistory).filter_by(chatbot_id=chatbot_id).count()
        
        conversation_list = []
        for conv in conversations:
            conversation_list.append({
                "id": conv.id,
                "query": conv.query,
                "response": conv.response,
                "created_at": conv.created_at.isoformat() if hasattr(conv, 'created_at') and conv.created_at else None
            })
        
        return {
            "conversations": conversation_list,
            "pagination": {
                "total": total_conversations,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_conversations
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversations: {str(e)}")
    finally:
        session.close()