import "./ResultList.css"
import * as React from 'react';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import ListSubheader from '@mui/material/ListSubheader';

type ResultListProps = {
    header: string
    list: Array<string>
    onListClick: (word: string) => void
}


export const ResultList = ({list, header, onListClick}: ResultListProps) => {
    return (
        <Box className="result-list">
            <nav aria-label="wordlist">
                <List dense={true} subheader={<li/>}>
                    <ListSubheader sx={{bgcolor: "#94999e"}}>{header}</ListSubheader>
                    {
                        list.map((word, index) => (
                            <ListItem key={index} disablePadding>
                                <ListItemButton onClick={_ => onListClick(word)}>
                                    <ListItemText primary={index + 1 + ". " + word.toUpperCase()}/>
                                </ListItemButton>
                            </ListItem>
                        ))
                    }
                </List>
            </nav>
        </Box>
    )
}