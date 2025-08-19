from fastapi import WebSocket
import asyncio
import json
from typing import Dict, List


class AsyncQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.user_websockets: Dict[str, List[WebSocket]] = {}
    
    async def add_websocket(self, websocket: WebSocket, username: str):
        if username not in self.user_websockets:
            self.user_websockets[username] = []
        self.user_websockets[username].append(websocket)
    
    async def remove_websocket(self, websocket: WebSocket, username: str):
        if username in self.user_websockets:
            if websocket in self.user_websockets[username]:
                self.user_websockets[username].remove(websocket)
            if not self.user_websockets[username]:
                del self.user_websockets[username]
    
    async def broadcast_js_to_user(self, js_code: str, username: str):
        if username in self.user_websockets:
            for websocket in self.user_websockets[username][:]:
                try:
                    await websocket.send_json({
                        "event": "execute-js",
                        "payload": {"code": js_code}
                    })
                except:
                    self.user_websockets[username].remove(websocket)
    
    async def broadcast_html_to_user(self, html: str, username: str):
        if username in self.user_websockets:
            for websocket in self.user_websockets[username][:]:
                try:
                    await websocket.send_json({
                        "event": "render", 
                        "payload": {"html": html}
                    })
                except:
                    self.user_websockets[username].remove(websocket)
    
    async def broadcast_js(self, js_code: str):
        """Broadcast to all users - kept for compatibility"""
        for username in self.user_websockets:
            await self.broadcast_js_to_user(js_code, username)
    
    async def broadcast_html(self, html: str):
        """Broadcast to all users - kept for compatibility"""
        for username in self.user_websockets:
            await self.broadcast_html_to_user(html, username)