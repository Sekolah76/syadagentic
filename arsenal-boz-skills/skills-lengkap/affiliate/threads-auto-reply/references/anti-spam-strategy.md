# Threads Auto-Reply Anti-Spam Strategy (v6.3)

To prevent Threads/Instagram from flagging the account as spam (integrity blocking, action blocked, or volume restrictions), follow this strategy:

## 1. No Direct Links in Comments
- **Rule:** Never insert Shopee affiliate links (`s.shopee.co.id`) directly in the comment body.
- **Why:** Algorithmic scanners immediately flag external commerce links in comments as bot behavior.
- **Solution:** Use soft-redirect phrasing directing the poster/readers to the account bio:
  - *"Wah sama bgt kak, aku dulu jerawatan parah... Kalo mau tau aku spill link-nya di bio aku ya 😭"*
  - *"Sumpah ngerti banget rasanya lepek 😩... Coba deh cek link di profil aku kak."*

## 2. Human Typing Delays
- **Rule:** Pause between action steps to mimic human speeds.
- **Implementation:** Wait `15` to `30` seconds randomly using `time.sleep()` after injecting the comment text via `execCommand` before triggering the click on the submit button.

## 3. Conversational Problem Keywords
- **Rule:** Target genuine user struggles instead of structured queries.
- **Keywords to use:** Use terms like *"jerawat parah banget"*, *"rambut rontok parah"*, *"makeup crack banget"* rather than search patterns like *"rekomendasi skincare"*.

## 4. Aggressive Rate Limiting
- **Rule:** Scale down reply frequencies to the bare minimum.
- **Schedule:** Run the reply cron job at a maximum interval of `every 24h` (once a day) to maintain account trust scores.
