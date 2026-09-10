# REST & WebSocket API Specification

## 1. Authentication & User Profile
- `POST /api/v1/auth/apple`: Sign in with Apple identity token verification, issue JWT pair.
- `POST /api/v1/auth/refresh`: Rotate refresh token and issue new access token.
- `GET /api/v1/users/me`: Current listener profile, subscription tier, and privacy flags.
- `PATCH /api/v1/users/me/privacy`: Toggle history collection, analytics participation, and social visibility.
- `DELETE /api/v1/users/me`: Account deletion and data purge request (GDPR/CCPA compliance).

## 2. Catalog & Discovery
- `GET /api/v1/catalog/tracks/{id}`: Detailed track metadata, audio quality tiers, lyrics.
- `GET /api/v1/catalog/albums/{id}`: Album tracklist, artwork, credits, lossless specifications.
- `GET /api/v1/catalog/artists/{id}`: Artist profile, top tracks, discography, related artists, support tiers.
- `GET /api/v1/catalog/search?q={query}&type={track,artist,album}&genre={id}&limit=30`: Typo-tolerant search prioritizing relevance over simple popularity.

## 3. Recommendation Engine (SRS FR-005, FR-006, FR-007)
- `POST /api/v1/recommendations/candidates`:
  - **Payload**:
    ```json
    {
      "variance_level": 0.65,
      "seed_track_ids": ["trk_123", "trk_456"],
      "limit": 50,
      "exclude_track_ids": ["trk_789"]
    }
    ```
  - **Response**: Candidate tracks scored with familiarity, novelty, and clear algorithmic explanation tags:
    ```json
    {
      "variance_level": 0.65,
      "mode": "exploratory",
      "items": [
        {
          "track_id": "trk_901",
          "title": "Midnight City Lights",
          "artist_name": "Solaris Echo",
          "score": 0.88,
          "explanation": "Selected for matching tempo (124 BPM) and resonant synth textures"
        }
      ]
    }
    ```

## 4. Playback & Streaming (SRS FR-003, FR-004)
- `GET /api/v1/stream/{track_id}`:
  - Validates user subscription tier & license availability.
  - Returns signed HLS manifest or direct progressive stream URL with exact audio format header (`X-Delivered-Bit-Depth: 24`, `X-Delivered-Sample-Rate: 96000`, `X-Audio-Codec: FLAC`).

## 5. Library & Hybrid Reconciliation (SRS FR-013, FR-014, FR-015)
- `GET /api/v1/library/items`: Fetch synchronized user library.
- `POST /api/v1/library/reconcile`:
  - **Payload**: Batch of local audio file metadata (ISRC, SHA-256, duration, artist, title, album).
  - **Response**: Reconciliation resolution (matched catalog track ID or local fallback marker).

## 6. Social Listening Rooms & Collaborative Queue (SRS FR-021, FR-022)
- `POST /api/v1/rooms`: Create listening room with permissions (`host_only`, `moderators`, `everyone`).
- `GET /api/v1/rooms/{id}`: Room details and active participant roster.
- `WebSocket /ws/rooms/{room_id}`:
  - Event `PLAYBACK_STATE_UPDATE`: Sync timestamp, track ID, and playing status.
  - Event `QUEUE_ITEM_ADDED`: Real-time queue insertion.
  - Event `QUEUE_ITEM_VOTE`: Collaborative voting to reorder queue dynamically.

## 7. Artist Economy & User-Centric Accounting (SRS FR-019, FR-020)
- `POST /api/v1/artists/{id}/support`: Fan direct tipping or membership transaction.
- `GET /api/v1/royalties/user-statement`: Monthly breakdown showing exact allocation of the listener's subscription fee to the artists they played.
