import Board from "./Board";
import React from "react";

type GameProps = {
    arr: Array<[string, string]>
    onClick: (index: number) => void
    current: number
}


function Game() {

    let props: GameProps = {
        arr: new Array(5 * 6).fill(["a", "b"]),
        onClick: i => console.log(i),
        current: 0,
    }

    return (
        <div className="game-board">
            <div className="word-list">
                <Board array={props.arr} onClick={props.onClick} current={props.current}/>
            </div>
            <div className="game-keyboard">
                <p>q</p>
                <p>z</p>
            </div>

        </div>
    )
}


export default Game