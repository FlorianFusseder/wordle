import Key from "./Key";
import React from "react";

type KeyBoardProps = {
    onClick: (value: string) => void
}

const KeyBoard = ({onClick}: KeyBoardProps) => {

    function renderKey(value: string, classNameStr?: string) {
        return <Key value={value} onClick={() => onClick(value)} classNameStr={classNameStr}/>
    }

    return (
        <div className="key-board">
            <div className="key-board-row">
                {renderKey("q")}
                {renderKey("w")}
                {renderKey("e")}
                {renderKey("r")}
                {renderKey("t")}
                {renderKey("y")}
                {renderKey("u")}
                {renderKey("i")}
                {renderKey("o")}
                {renderKey("p")}
                {renderKey("ü")}
            </div>
            <div className="key-board-row">
                {renderKey("a")}
                {renderKey("s")}
                {renderKey("d")}
                {renderKey("f")}
                {renderKey("g")}
                {renderKey("h")}
                {renderKey("j")}
                {renderKey("k")}
                {renderKey("l")}
                {renderKey("ö")}
                {renderKey("ä")}
            </div>
            <div className="key-board-row">
                {renderKey("z")}
                {renderKey("x")}
                {renderKey("c")}
                {renderKey("v")}
                {renderKey("b")}
                {renderKey("n")}
                {renderKey("m")}
                {renderKey("delete", "action-button")}
            </div>
            <div className="key-board-row">
                {renderKey("submit", "action-button")}
            </div>
        </div>
    )
}


export default KeyBoard