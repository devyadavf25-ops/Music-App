"""
User-Centric Revenue Allocation Engine (SRS FR-020, Risk 2).
Calculates exact royalty distributions by attributing each individual listener's net
subscription pool directly to the artists they listened to during the billing period,
rather than dumping all revenues into a market-share pro-rata pool.
"""

from typing import List, Dict, Any
from ..models.entities import ListeningEvent, Subscription, ArtistSupport


class UserCentricRoyaltyCalculator:
    PLATFORM_FEE_RATE = 0.30  # 30% platform infrastructure & operation fee

    @classmethod
    def calculate_user_royalty_distribution(
        cls,
        subscription: Subscription,
        listening_events: List[ListeningEvent],
        direct_tips: List[ArtistSupport] = None
    ) -> Dict[str, Any]:
        """
        Allocates user net subscription = (Monthly Fee * (1 - PlatformFee))
        proportionally by stream count of eligible completed tracks.
        """
        net_royalty_pool = subscription.monthly_amount * (1.0 - cls.PLATFORM_FEE_RATE)
        
        # Filter valid streams (at least 30 seconds or marked completed)
        valid_streams = [e for e in listening_events if e.duration_listened_seconds >= 30 or e.completed]
        total_valid_streams = len(valid_streams)

        artist_stream_counts: Dict[str, int] = {}
        for stream in valid_streams:
            artist_stream_counts[stream.artist_id] = artist_stream_counts.get(stream.artist_id, 0) + 1

        artist_payouts: List[Dict[str, Any]] = []

        if total_valid_streams > 0:
            for artist_id, count in artist_stream_counts.items():
                stream_fraction = count / total_valid_streams
                subscription_payout = net_royalty_pool * stream_fraction
                artist_payouts.append({
                    "artist_id": artist_id,
                    "stream_count": count,
                    "stream_share_percent": round(stream_fraction * 100, 2),
                    "subscription_revenue": round(subscription_payout, 4),
                    "direct_support_revenue": 0.0,
                    "total_payout": round(subscription_payout, 4)
                })

        # Add direct tips / fan support
        if direct_tips:
            tip_map: Dict[str, float] = {}
            for tip in direct_tips:
                # 90% direct tip to artist (10% payment processor & handling)
                net_tip = tip.amount * 0.90
                tip_map[tip.artist_id] = tip_map.get(tip.artist_id, 0.0) + net_tip

            # Merge into payouts
            existing_artists = {p["artist_id"]: p for p in artist_payouts}
            for artist_id, tip_amount in tip_map.items():
                if artist_id in existing_artists:
                    existing_artists[artist_id]["direct_support_revenue"] = round(tip_amount, 2)
                    existing_artists[artist_id]["total_payout"] = round(
                        existing_artists[artist_id]["subscription_revenue"] + tip_amount, 4
                    )
                else:
                    artist_payouts.append({
                        "artist_id": artist_id,
                        "stream_count": 0,
                        "stream_share_percent": 0.0,
                        "subscription_revenue": 0.0,
                        "direct_support_revenue": round(tip_amount, 2),
                        "total_payout": round(tip_amount, 4)
                    })

        artist_payouts.sort(key=lambda x: x["total_payout"], reverse=True)

        return {
            "user_id": subscription.user_id,
            "billing_period_gross": subscription.monthly_amount,
            "currency": subscription.currency,
            "net_distributable_royalty_pool": round(net_royalty_pool, 2),
            "total_streams_evaluated": total_valid_streams,
            "unique_artists_funded": len(artist_payouts),
            "artist_breakdown": artist_payouts
        }
