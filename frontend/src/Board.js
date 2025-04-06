import React, { useEffect, useState } from "react";
import { Stage, Sprite, Container } from "@pixi/react";
import * as PIXI from "pixi.js";
import axios from "axios";

const BOARD_IMAGE = "/SKM_C30825032118180.jpg";  // Coloque a imagem do tabuleiro aqui
const PLAYER_ICON = "/pawn.jpeg";   // Ícone do peão

// Posições pré-definidas dos pontos no tabuleiro
const positions = {
    1: { x: 100, y: 200 },
    2: { x: 250, y: 300 },
    3: { x: 400, y: 150 },
    // Adicione todas as posições do tabuleiro...
};

export default function Board() {
    const [players, setPlayers] = useState([]);

    // Busca os jogadores da API
    useEffect(() => {
        axios.get("http://127.0.0.1:8000/players")
            .then(response => setPlayers(response.data))
            .catch(error => console.error("Erro ao buscar jogadores", error));
    }, []);

    // Mover jogador (simplesmente para testar)
    const movePlayer = async (playerId, newPosition) => {
        await axios.post("http://127.0.0.1:8000/move-player", { player_id: playerId, new_position: newPosition });
        setPlayers(players.map(p => (p.id === playerId ? { ...p, position: newPosition } : p)));
    };

    return (
        <Stage width={800} height={600} options={{ backgroundColor: 0x1099bb }}>
            {/* Tabuleiro */}
            <Sprite image={BOARD_IMAGE} x={0} y={0} width={800} height={600} />

            {/* Jogadores */}
            {players.map(player => (
                <Container key={player.id} x={positions[player.position]?.x || 0} y={positions[player.position]?.y || 0}>
                    <Sprite
                        image={PLAYER_ICON}
                        width={40} height={40}
                        interactive={true}
                        pointerdown={() => movePlayer(player.id, player.position + 1)} // Move o peão ao clicar
                    />
                </Container>
            ))}
        </Stage>
    );
}
