import * as React from 'react'
import './Square.css'
import {ChangeEvent, KeyboardEvent} from "react";

interface SquareProps {
    value: string,
    code: string | null,
    onChange: (event: ChangeEvent<HTMLInputElement>) => void
    onKeyUp: (event: KeyboardEvent<HTMLInputElement>) => void
    current: boolean
}

const Square = ({value, code, onChange, onKeyUp, current}: SquareProps) => {

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

    const input_ref = React.useRef<HTMLInputElement>(null);
    React.useEffect(() => {
        if (input_ref.current && current) {
            input_ref.current.focus();
        }
    });

    return (
        <input
            type="text"
            className={getClassString()}
            maxLength={1}
            ref={input_ref}
            value={value}
            onChange={onChange}
            onKeyUp={onKeyUp}
            pattern="[A-ZÄÖÜ]"
        />
    )
}


export default Square