import * as React from 'react'
import './Square.css'
import {ChangeEvent, KeyboardEvent} from "react";

interface SquareProps {
    value: string
    code: string | null
    onChange: (event: ChangeEvent<HTMLInputElement>) => void
    onKeyUp: (event: KeyboardEvent<HTMLInputElement>) => void
    current: boolean
    current_ref: React.RefObject<HTMLInputElement>
}

const Square = ({value, code, onChange, onKeyUp, current, current_ref}: SquareProps) => {

    function getClassString() {
        let classString: string = current ? "square current" : "square"

        switch (code) {
            case "f":
                classString += " not_contained"
                break;
            case "t":
                classString += " correct"
                break;
            case "c":
                classString += " contained"
                break;
            default:
                break
        }

        return classString
    }

    return (
        <input
            type="text"
            className={getClassString()}
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
    )
}


export default Square