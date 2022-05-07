import React from 'react'
import {Game} from './components/Game'
import './App.css';
import Box from '@mui/material/Box'
import Chip from '@mui/material/Chip'
import Stack from "@mui/material/Stack";


function App() {
    return (
        <Box className="App">
            <link
                rel="stylesheet"
                href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
            />
            <link
                rel="stylesheet"
                href="https://fonts.googleapis.com/icon?family=Material+Icons"
            />
            <header className="App-header">
                <Game/>
                <Stack className="sticky-footer" direction="row" justifyContent="center">
                    <Chip label={process.env.REACT_APP_NAME}/>
                    <Chip label={"v" + process.env.REACT_APP_VERSION}/>
                    <Chip component="a" href="mailto:florianfusseder@gmail.com" clickable label="florianfusseder@gmail.com"/>
                    <Chip component="a" href="https://github.com/FlorianFusseder/wordle" clickable label="Github"/>
                </Stack>
            </header>
        </Box>
    );
}

export default App;
