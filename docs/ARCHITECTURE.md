# System Architecture & Technical Specifications

## 1. Architectural Philosophy (SRS §2, §7)
The platform is built on a **hybrid architectural model**:
- **iOS / iPadOS Native Client**: Owns the presentation, real-time playback engine, privacy-preserving personalization, local library indexing, offline encrypted cache, and hardware-accelerated capabilities (Core Haptics, AVFoundation, Core ML, SwiftData, SharePlay).
- **Cloud Backend Layer**: Owns catalog-scale operations, multi-attribute indexing, candidate generation, sync & reconciliation, rights management, secure audio tokenization/distribution, and commercial accounting (user-centric royalties).

```
+-------------------------------------------------------------------------------+
|                             iOS / iPadOS Client                               |
|                                                                               |
|  +-------------------------+  +---------------------+  +-------------------+  |
|  |     SwiftUI Views       |  | Core ML Ranker      |  | AVFoundation      |  |
|  | (Home, Search, Player)  |  | (On-Device Vectors) |  | (Lossless Engine) |  |
|  +------------+------------+  +----------+----------+  +---------+---------+  |
|               |                          |                       |            |
|  +------------v--------------------------v-----------------------v---------+  |
|  |                   App State & ViewModels (Swift Actors)                 |  |
|  +-----------------------------------+-------------------------------------+  |
|                                      |                                        |
|  +-----------------------------------v-------------------------------------+  |
|  |                  SwiftData Store & Local File Indexer                   |  |
|  +-----------------------------------+-------------------------------------+  |
+--------------------------------------|----------------------------------------+
                                       | HTTPS (TLS 1.3) / WebSockets
+--------------------------------------v----------------------------------------+
|                              Cloud Backend                                    |
|                                                                               |
|  +--------------------+  +--------------------+  +-------------------------+  |
|  | Catalog & Search   |  | Rec Candidate Gen  |  | Hybrid Sync & Rights    |  |
|  | (Postgres/Vectors) |  | (Acoustic Clusters)|  | (ISRC Reconciliation)   |  |
|  +--------------------+  +--------------------+  +-------------------------+  |
|  +--------------------+  +--------------------+  +-------------------------+  |
|  | Social & SharePlay |  | User-Centric Pay   |  | Audio CDN / Token Svc   |  |
|  | (WebSockets Rooms) |  | (Royalty Engine)   |  | (Signed DRM / Stream)   |  |
|  +--------------------+  +--------------------+  +-------------------------+  |
+-------------------------------------------------------------------------------+
```

---

## 2. Core Functional Pillars

### 2.1 Recommendation Variance Slider & Algorithmic Agency (FR-005, FR-006, FR-007)
Rather than an opaque feed, the listener controls the exploration parameter $\lambda \in [0.0, 1.0]$:
$$\text{Score}(t) = (1 - \lambda) \cdot S_{\text{familiarity}}(t, u) + \lambda \cdot S_{\text{novelty}}(t, u) - P_{\text{repetition}}(t, u)$$
- **0–20% (Familiar)**: High weight on user listening history, frequent artists, favored genres ($P_{\text{repetition}}$ dampens recent 30-day plays).
- **21–50% (Balanced)**: Blends familiar favorites with organically related artists.
- **51–80% (Exploratory)**: Surfacing adjacent subgenres, collaborative recommendations, and rising artists.
- **81–100% (Strong Discovery)**: Maximizes acoustic novelty and surfaces the catalog's long tail ($<50\text{k}$ lifetime plays), with strict penalties on artist and genre repetition.

Each track carries an **Algorithmic Transparency Tag**:
- *"Recommended because you frequently listen to Arctic Monkeys"*
- *"Selected for matching tempo and key (120 BPM, C Major)"*
- *"Deep discovery: Similar acoustic timbre to your favorite ambient tracks"*

### 2.2 Four Distinct Shuffle Modes (FR-008)
1. **Standard Shuffle**: Modern pseudo-random Fisher-Yates with a lookahead buffer preventing artist/album repeats within a 5-track window.
2. **True Shuffle**: Strict uniform statistical distribution with guaranteed non-consecutive play of identical tracks.
3. **Smart Shuffle**: Acoustic harmonic transition matching (BPM compatibility $\pm 10\%$, camelot wheel harmonic mixing) balanced with user preferences.
4. **Discovery Shuffle**: Reorders queue to alternate 1 known track with 2 high-scoring unfamiliar tracks.

### 2.3 Hybrid Library Reconciliation (FR-013, FR-014)
When a user imports local audio files (MP3, AAC, FLAC, WAV, ALAC):
1. **Stage 1 (Exact)**: Compute SHA-256 hash against known local cache.
2. **Stage 2 (ISRC Match)**: Extract embedded ID3/Vorbis ISRC tag and match against global catalog master.
3. **Stage 3 (Fingerprint & Metadata)**: Match normalized Artist + Title + Album + Track Duration ($\pm 1.5\text{s}$) to merge streaming lyrics, artist profiles, and high-res streaming alternatives while preserving custom user metadata.

### 2.4 Audiophile Honesty (FR-004, FR-023)
The player inspects hardware output and actual delivered stream buffer:
- Reports accurate audio metrics: `24-bit / 96 kHz ALAC`, `Lossless 16-bit / 44.1 kHz FLAC`, or `AAC 256 kbps (Downsampled)`.
- If an external DAC or Bluetooth route does not support high-res lossless, the UI clearly reflects the hardware downsample route.

### 2.5 User-Centric Revenue Allocation (FR-020)
Instead of a pro-rata pool where mega-stars take the majority of subscription fees regardless of individual listening, the user-centric model allocates a user's net subscription fee directly to the specific artists that user streamed during the billing cycle:
$$\text{Artist Share} = \sum_{u \in U} \left( \text{Net Subscription}_u \times \frac{\text{Streams of Artist by } u}{\text{Total Streams by } u} \right)$$
