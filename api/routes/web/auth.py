from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse

from api.auth import authenticate_user, create_access_token
from api.templates import templates
from api.exceptions.auth import AuthenticationException

router = APIRouter()


@router.post("/web-token", response_class=HTMLResponse)
def login_web_form(
    request: Request, 
    response: Response,
    username: str = Form(...), 
    password: str = Form(...)
):
    """
    Endpoint für Web-Authentifizierung via Login-Formular.
    Setzt ein Cookie mit dem Token und liefert eine HTML-Antwort zurück.
    """
    user = authenticate_user(username, password)
    if not user:
        # HTML-Fragment für Fehlermeldung zurückgeben
        return templates.TemplateResponse(
            "login_error.html",
            {"request": request, "message": "Ungültiger Benutzername oder Passwort"}
        )
    
    # Token erstellen und als Cookie setzen
    access_token_expires = timedelta(minutes=60)  # Längere Gültigkeit für Web-Sessions
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value, "person_id": str(user.person_id)},
        expires_delta=access_token_expires
    )
    
    # Cookie setzen
    response.set_cookie(
        key="appointments_token",
        value=access_token,
        httponly=True,
        max_age=3600,  # 1 Stunde
        samesite="lax",
        secure=False  # Auf True setzen in Produktion mit HTTPS
    )
    
    # HTML-Fragment für Erfolgsmeldung zurückgeben, das die Seite neu lädt
    return """
    <div class="bg-green-800 text-white p-3 rounded-md mb-4">
        Erfolgreich angemeldet! Die Seite wird neu geladen...
    </div>
    <script>
        setTimeout(function() {
            window.location.reload();
        }, 1000);
    </script>
    """

@router.get("/logout", response_class=HTMLResponse)
def logout(request: Request, response: Response):
    """
    Löscht das Authentifizierungs-Cookie und leitet zurück zur Startseite.
    """
    response.delete_cookie(key="appointments_token")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                background-color: #121212; /* Entspricht --dark-900 */
                margin: 0;
                padding: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .loader {
                border: 4px solid #2D2D2D; /* --dark-700 */
                border-top: 4px solid #7B1CD7; /* --primary-600 */
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="loader"></div>
        <script>
            window.location.href = "/";
        </script>
    </body>
    </html>
    """
