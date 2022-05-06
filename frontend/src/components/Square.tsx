import * as React from 'react'
import './Square.css'
import {ChangeEvent, KeyboardEvent, MouseEvent} from "react";
import {Code, Position} from "./Game"
import Box from "@mui/material/Box";

interface SquareProps {
    key_: string
    value: string
    code: Code
    onChange: (event: ChangeEvent<HTMLInputElement>) => void
    onKeyUp: (event: KeyboardEvent<HTMLInputElement>) => void
    current: boolean
    current_ref: React.RefObject<HTMLInputElement>
    change_color_to_code: (event: MouseEvent<HTMLButtonElement>, code: Code, position: Position) => void
    self_position: Position
}

const Square = ({
                    key_,
                    value,
                    code,
                    onChange,
                    onKeyUp,
                    current,
                    current_ref,
                    change_color_to_code,
                    self_position
                }: SquareProps) => {

    function getCodeString() {
        let classString: string = "coded"

        switch (code) {
            case Code.green:
                classString = " correct " + classString
                break;
            case Code.yellow:
                classString = " contained " + classString
                break;
            case Code.grey:
                classString = " not_contained " + classString
                break;
            case Code._undefined:
                classString = " un" + classString
        }

        return classString
    }

    return (
        <Box className={"square-container" + (current ? " current" : "") + (value ? "" : " empty") + getCodeString()}>
            <Box className="color-picker-buttons">
                <button className="green" onClick={event => change_color_to_code(event, Code.green, self_position)}/>
                <button className="yellow" onClick={event => change_color_to_code(event, Code.yellow, self_position)}/>
                <button className="grey" onClick={event => change_color_to_code(event, Code.grey, self_position)}/>
            </Box>
            <input
                key={key_}
                type="text"
                className={(current ? "square current" : "square") + getCodeString()}
                maxLength={1}
                ref={current ? current_ref : null}
                disabled={!current}
                value={value}
                onChange={onChange}
                onKeyUp={onKeyUp}
                onBlur={event => {
                    event.preventDefault()
                    setTimeout(() => {
                        if (current_ref.current) {
                            current_ref.current.focus()
                            current_ref.current.select()
                        }
                    }, 1)
                }}
                pattern="[A-ZÄÖÜ]"
            />
        </Box>
    )
}


export default Square