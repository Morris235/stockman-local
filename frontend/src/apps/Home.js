import React from 'react';
import { Link } from 'react-router-dom';

// 새로운 가치를 만드는거야
export default function Home () {

    return (
        <div>
            <h1>Hi it's my first React Home!</h1>
                <ul>
                    <li>
                        <Link to="/companylist">companyBoard</Link>
                    </li>
                </ul>
        </div>
    );
}