import React from 'react';
import { BrowserRouter as Router,
    Route, 
    Link, 
    Switch } from 'react-router-dom';

/* components */
import CompanyBoard from './CompanyBoard';
import NotFound from './NotFound';
import Home from './Home';

export default function Routing () {

    // url 이동할 때 이전 앱의 상태값은 날라가지 않는다.
    return (
        <Router>
            <div>
                <Link to="/"><h2>Stockman</h2></Link>

                <Switch>
                    <Route path="/"  exact={true}><Home /></Route>
                    <Route path="/companylist"><CompanyBoard /></Route>
                    <Route path="*"><NotFound /></Route>
                </Switch>
            </div>
        </Router>
    );
}