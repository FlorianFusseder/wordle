import Key from "./Key";
import React from "react";
import Stack from '@mui/material/Stack'


type KeyBoardProps = {
    onClick: (value: string) => void
}

const KeyBoard = ({onClick}: KeyBoardProps) => {

    function renderKey(value: string, classNameStr?: string) {
        return <Key
            value={value.toLowerCase()}
            onClick={() => onClick(value.toUpperCase())}
            classNameStr={classNameStr}
        />
    }

    return (
        <React.Fragment>
            <Stack direction="row" spacing={.2} justifyContent="center" marginBottom={.2}>
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
            </Stack>
            <Stack direction="row" spacing={.2} justifyContent="center" marginBottom={.2}>
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
            </Stack>
            <Stack direction="row" spacing={.2} justifyContent="center" marginBottom={.2}>
                {renderKey("z")}
                {renderKey("x")}
                {renderKey("c")}
                {renderKey("v")}
                {renderKey("b")}
                {renderKey("n")}
                {renderKey("m")}
                {renderKey("delete", "action-button")}
            </Stack>
            <Stack direction="row" justifyContent="center">
                {renderKey("submit", "action-button")}
            </Stack>
        </React.Fragment>
    )
}


export default KeyBoard