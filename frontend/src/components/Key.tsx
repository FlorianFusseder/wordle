import * as React from 'react'
import './Key.css'

interface KeyProps {
    value: string,
    onClick: () => void
    classNameStr?: string
}

const Key = ({value, onClick, classNameStr}: KeyProps) => (
    <button
        className={["keyboard-button", classNameStr].join(" ")}
        onClick={onClick}>
        {value}
    </button>
)


export default Key