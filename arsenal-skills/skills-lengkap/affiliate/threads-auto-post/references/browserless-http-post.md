# Browserless HTTP Publish Engine (v2.0)

## Overview
Metode posting Threads secara browserless menggunakan HTTP requests langsung ke Instagram/Threads private API. Menghindari overhead RAM, masalah window focus Chrome, dan bentrokan AppleScript.

## API Endpoints

### 1. Image Upload (Rupload)
```http
POST https://www.threads.com/rupload_igphoto/fb_uploader_{upload_id}
```
* **Headers**:
  * `X-Instagram-Rupload-Params`: `{"is_sidecar":"0","is_threads":"1","media_type":1,"upload_id":"{upload_id}","upload_media_height":H,"upload_media_width":W}`
  * `Content-Type`: `image/jpeg`
  * `X-Entity-Length`: Ukuran file gambar (bytes)
  * `X-Entity-Name`: `fb_uploader_{upload_id}`
  * `Offset`: `0`
* **Response**: `{"upload_id":"...","status":"ok"}`

### 2. Configure Post (Image / Root)
Menggunakan endpoint feed untuk mendaftarkan post dengan gambar:
```http
POST https://www.threads.com/api/v1/media/configure_text_post_app_feed/
```
* **Content-Type**: `application/x-www-form-urlencoded;charset=UTF-8`
* **Headers Penting**:
  * `X-IG-App-ID`: `238260118697367` (Threads Web Client ID)
  * `X-ASBD-ID`: `359341`
  * `X-Bloks-Version-Id`: `2b9ad6476ac3644813949168e1750220dba5d9eaea4b3fee7dcff7550d48c896`
* **Payload Kunci**:
  * `upload_id`: ID upload dari rupload response
  * `is_threads`: `true`
  * `text_post_app_info`: JSON berisi `reply_control` dan `self_thread_context_id` (UUID baru)

### 3. Configure Post (Text / Reply)
Untuk text-only root post atau balasan berantai (chain replies):
```http
POST https://www.threads.net/api/v1/media/configure_text_only_post/
```
* **Payload Kunci**:
  * `replied_to_media_id`: PK dari post sebelumnya (untuk chain thread)
  * `text_post_app_info`: `{"reply_control":0,"reply_id":"{parent_pk}","is_reply":true,"reply_to_author":"{author_uid}"}`

## Cookie & Auth Requirements
Urllib/requests membutuhkan integrasi cookie Threads native:
1. Ambil cookie langsung dari SQLite DB Chrome Profile 16 (`.threads.com` dan `.instagram.com`).
2. Gabungkan (merge) cookie tersebut. Cookie Threads (`ds_user_id` / `sessionid`) wajib menimpa cookie Instagram agar tidak memicu HTTP 500 / 400.

## Failures & Pitfalls
* **HTTP 500 di Configure Feed**: Sering terjadi jika cookie expired atau session ID tidak ter-refresh dari threads.com secara native. Lakukan preflight check / refresh cookie via camoufox/AppleScript jika gagal.
* **HTTP 400 "Incorrect state machine"**: Terjadi jika payload `publish_mode` atau `text_post_app_info` tidak terformat JSON secara strict atau parameter media tercampur dengan text-only endpoint.
