// services/websocket.ts

export class WebSocketService {
  private socket: WebSocket | null = null;

  connect(onMessage: (data: any) => void) {
    this.socket = new WebSocket(`ws://localhost:8000/api/documents/ws`);

    this.socket.onopen = () => {
      console.log("Connected");
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.socket.onclose = () => {
      console.log("Disconnected");
      this.socket = null;
    };
  }

  send(data: Blob | ArrayBuffer | string) {
    this.socket?.send(data);
  }

  disconnect() {
    this.socket?.close();
  }
}
