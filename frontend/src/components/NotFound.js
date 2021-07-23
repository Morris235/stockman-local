import React from 'react';
import { useLocation } from 'react-router-dom';

export default function NotFound () {
    let location = useLocation();

    return (
        <>
        <h1>Not Found Page <code>{location.pathname}</code> </h1>
        </>
    );
}