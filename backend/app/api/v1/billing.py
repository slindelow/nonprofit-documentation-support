from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.core.security import get_current_user_id

router = APIRouter()


@router.get("/plans", summary="List available subscription plans")
async def list_plans():
    return {
        "plans": [
            {"id": "starter", "name": "Starter", "price_monthly": 99, "limits": {"grants": 20, "members": 3, "knowledge_docs": 20}},
            {"id": "growth", "name": "Growth", "price_monthly": 249, "limits": {"grants": 100, "members": 10, "knowledge_docs": 100}},
            {"id": "enterprise", "name": "Enterprise", "price_monthly": None, "limits": None},
        ]
    }


@router.post("/checkout", summary="Create a Stripe Checkout session")
async def create_checkout(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """Returns a Stripe Checkout URL for the selected plan."""
    return {"status": "not_implemented", "checkout_url": None}


@router.post("/portal", summary="Open Stripe Customer Portal")
async def billing_portal(user_id: Annotated[UUID, Depends(get_current_user_id)]):
    """Returns a Stripe Customer Portal URL for managing subscription."""
    return {"status": "not_implemented", "portal_url": None}


@router.post("/webhook", summary="Stripe webhook handler", include_in_schema=False)
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Handles Stripe events:
    - checkout.session.completed → activate subscription
    - customer.subscription.updated → update tier
    - customer.subscription.deleted → downgrade to free
    """
    return {"status": "not_implemented"}
