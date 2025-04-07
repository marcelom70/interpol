import { useState, useEffect, useRef } from "react";
import "./App.css";

const BOARD_IMAGE = "/board.jpeg";
// const backendUrl = process.env.REACT_APP_BACKEND_URL;
const backendUrl = import.meta.env.VITE_BACKEND_URL;

interface Player {
  client_id?: string; // Optional
  tickets: string[];
  type: string;
  nick?: string;
  color: string;
  current_spot: number;
  position: Record<string, number>;
}

export default function Board() {
  const boardRef = useRef<HTMLImageElement | null>(null);
  // const boardRef = useRef(null);
  //const boardRef = useRef<HTMLDivElement | null>(null);
  const [boardSize, setBoardSize] = useState({ width: 1, height: 1 });
  const [position, setPosition] = useState("");
  const [transport, setTransport] = useState("TAXI");
  const [showModal, setShowModal] = useState(true);
  const [nick, setNick] = useState("");
  const [playerColor, setPlayerColor] = useState("");
  const [isPlayerX, setIsPlayerX] = useState(false);
  const [player, setPlayer] = useState<Player[]>([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [playerList, setPlayerList] = useState("");
  const [players, setPlayers] = useState<Player[]>([]);
  const [randomValue] = useState(() => {
    console.log(`Log aqui dentro do useState (antes)!`);
    const retorno = Math.floor(Math.random() * 10000).toString();
    console.log(`Value returned ${retorno} of type ${typeof retorno}`);
    return retorno;
  });

  const handleStartGame = async () => {
    const playerData = {
      client_id: randomValue,
      nick,
      type: isPlayerX ? "X" : "O",
      color: isPlayerX ? "black" : "red",
      position: { x: 0.5, y: 0.5 },
    };

    try {
      console.log(`This is the url ${backendUrl} in add-player`);
      console.log("Backend URL:", import.meta.env.VITE_BACKEND_URL);
      const response = await fetch(`http://${backendUrl}:8000/add-player`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(playerData),
      });
      console.log(
        `THis is the value for randomValue ${randomValue} in add-player`
      );

      if (!response.ok) {
        throw new Error(
          "Error: " + JSON.parse(await response.text())["message"]
        );
      }

      const data = await response.json();
      setPlayerColor(data.player.color);
      setPlayer(data);
      console.log(`Player: ${player}`);
      setShowModal(false);
      setErrorMessage("");
    } catch (e) {
      console.error("Error while connecting to the API:", e);
      if (e instanceof Error) {
        setErrorMessage(e.message);
      } else {
        setErrorMessage("Unknown error");
      }
    }
  };

  useEffect(() => {
    const socket = new WebSocket(`ws://${backendUrl}:8000/ws`);

    socket.onopen = () => {
      console.log(`Connecting to the WebSocket: ${randomValue}!`);
      socket.send(JSON.stringify({ id: randomValue }));
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Message received:", data);
        setPlayerList(data["message"]);
        const actionPlayer = data["player"];

        setPlayers((prevPlayers) => {
          const existingPlayer = prevPlayers.find(
            (p) => p.nick === actionPlayer.nick
          );

          if (existingPlayer) {
            return prevPlayers.map((p) =>
              p.nick === actionPlayer.nick
                ? { ...p, position: actionPlayer.position }
                : p
            );
          } else {
            return [
              ...prevPlayers,
              {
                tickets: [],
                current_spot: 0,
                color: actionPlayer.color,
                type: actionPlayer.type,
                nick: actionPlayer.nick,
                position: {
                  x: actionPlayer.position["x"],
                  y: actionPlayer.position["y"],
                },
              },
            ];
          }
        });
      } catch (ex) {
        console.log(`Erro: ${ex}`);
      }
    };

    socket.onerror = (error) => {
      console.error("Error in WebSocket:", error);
    };

    socket.onclose = () => {
      console.log("Connection closed.");
    };

    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    function updateBoardSize() {
      if (boardRef.current) {
        setBoardSize({
          width: boardRef.current.clientWidth,
          height: boardRef.current.clientHeight,
        });
      }
    }

    window.addEventListener("resize", updateBoardSize);
    updateBoardSize();

    return () => window.removeEventListener("resize", updateBoardSize);
  }, []);

  const handleAskAI = async () => {
    console.log(`Position: ${parseInt(position)}`);
    const requestBody = {
      type: "",
      nick: "",
      color: "red",
      current_spot: parseInt(position),
      position: { x: 0, y: 0 },
    };

    try {
      const response = await fetch(`http://${backendUrl}:8000/ask-ai`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });
      console.log(`Value found ${randomValue} in ask-ai`);
      const data = await response.json();
      console.log("API response:", data);
      alert(`Interpol says: ${data}`);
    } catch (error) {
      console.error("Error while moving player:", error);
    }
  };

  const handleMove = async () => {
    if (!position) {
      alert("Insert a valid position");
      return;
    }

    if (parseInt(position) < 1 || parseInt(position) > 199) {
      alert("Insert a value between 1 and 199");
      return;
    }

    const requestBody = {
      player: {
        client_id: randomValue,
        type: "X",
        nick,
        color: "red",
        position: { x: 0, y: 0 },
      },
      new_spot: parseInt(position),
      modal_type: transport,
    };

    try {
      const response = await fetch(`http://${backendUrl}:8000/move`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });
      console.log(`Value found ${randomValue} in move`);
      const data = await response.json();
      console.log("API response:", data);
      alert(`Interpol says: ${data.message}`);
    } catch (error) {
      console.error("Error while moving player:", error);
    }
  };

  const startMatch = async () => {
    const requestBody = {
      client_id: randomValue,
      type: "X",
      nick: "",
      color: "red",
      position: { x: 0, y: 0 },
    };

    try {
      const response = await fetch(`http://${backendUrl}:8000/start-match`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });
      console.log(`Value found ${randomValue} in start-match`);
      const data = await response.json();
      console.log("API response:", data);
      alert(`Interpol says: ${data.message}`);
    } catch (error) {
      console.error("Error while moving player:", error);
    }
  };

  console.log(`Players count: ${players.length}`);
  return (
    <div style={{ position: "relative", width: "100%", textAlign: "center" }}>
      {/* MODAL */}
      {showModal && (
        <div style={modalStyles.overlay}>
          <div style={modalStyles.modal}>
            <h2>Informe seus dados</h2>
            <input
              type="text"
              placeholder="Insert your nickname"
              value={nick}
              onChange={(e) => setNick(e.target.value)}
              style={modalStyles.input}
            />
            <label style={modalStyles.label}>
              <input
                type="checkbox"
                checked={isPlayerX}
                onChange={() => setIsPlayerX(!isPlayerX)}
              />
              Would you like to be Player X?
            </label>
            {errorMessage && <p style={modalStyles.error}>{errorMessage}</p>}
            <button onClick={handleStartGame} style={modalStyles.button}>
              Enter
            </button>
          </div>
        </div>
      )}

      <img
        ref={boardRef}
        src={BOARD_IMAGE}
        alt="Board"
        style={{ width: "100%", height: "auto" }}
      />

      <div style={{ marginTop: "20px" }}>
        <label>{playerList}</label>
        <br />
        <label style={{ color: playerColor }}>
          <b>Player:</b> {nick}{" "}
        </label>
        <label>
          <b>Próxima célula:</b>
          <input
            type="number"
            value={position}
            onChange={(e) => setPosition(e.target.value)}
            style={{ marginLeft: "10px", padding: "5px" }}
          />
        </label>

        <label style={{ marginLeft: "20px" }}>
          <b>Modal de Transporte:</b>
          <select
            value={transport}
            onChange={(e) => setTransport(e.target.value)}
            style={{ marginLeft: "10px", padding: "5px" }}
          >
            <option value="TAXI">Taxi</option>
            <option value="BUS">Bus</option>
            <option value="METRO">Metro</option>
            {isPlayerX && <option value="HIDDEN">Hidden</option>}
          </select>
        </label>

        <button
          onClick={handleMove}
          style={{
            marginLeft: "20px",
            padding: "8px 15px",
            background: "blue",
            color: "white",
            border: "none",
            cursor: "pointer",
          }}
        >
          Move
        </button>

        <button
          onClick={handleAskAI}
          style={{
            marginLeft: "20px",
            padding: "8px 15px",
            background: "blue",
            color: "white",
            border: "none",
            cursor: "pointer",
          }}
        >
          ?
        </button>

        {isPlayerX && (
          <button
            onClick={startMatch}
            style={{
              marginLeft: "20px",
              padding: "8px 15px",
              background: "blue",
              color: "white",
              border: "none",
              cursor: "pointer",
            }}
          >
            Start
          </button>
        )}
      </div>

      {players.map((player: Player) => (
        <div
          key={player.nick}
          style={{
            position: "absolute",
            top: `${player.position.y * boardSize.height}px`,
            left: `${player.position.x * boardSize.width}px`,
            transform: "translate(-50%, -50%)",
            width: "20px",
            height: "20px",
            borderRadius: "50%",
            border: `5px solid ${player.color}`,
            backgroundColor: "transparent",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        />
      ))}
    </div>
  );
}

const modalStyles: {
  overlay: React.CSSProperties;
  modal: React.CSSProperties;
  input: React.CSSProperties;
  label: React.CSSProperties;
  button: React.CSSProperties;
  error: React.CSSProperties;
} = {
  overlay: {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  modal: {
    backgroundColor: "#fff",
    padding: "20px",
    borderRadius: "10px",
    textAlign: "center",
  },
  input: {
    width: "80%",
    padding: "10px",
    margin: "10px 0",
  },
  label: {
    display: "block",
    margin: "10px 0",
  },
  button: {
    backgroundColor: "#28a745",
    color: "#fff",
    border: "none",
    padding: "10px 15px",
    cursor: "pointer",
    borderRadius: "5px",
  },
  error: {
    color: "red",
    fontSize: "14px",
  },
};
