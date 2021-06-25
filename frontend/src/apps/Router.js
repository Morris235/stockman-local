import React from 'react';
import { BrowserRouter as Router,
    Route, 
    Link, 
    Switch } from 'react-router-dom';


/* components */
import CompanyBoard from './CompanyBoard';
import NotFound from './NotFound';
import Home from './Home';
import TitleBar from '../components/TitleBar';

export default function Routing () {

    // url 이동할 때 이전 앱의 상태값은 날라가지 않는다.
    // 개발진행이 멈칫할때는 이해 안되는 부분 파악해서 바로 공부하기
    // 현재 문제점 컴포넌트 자체에 링크를 걸어버려서 해당 컴포넌트 안에 어떤 요소가 있던 클릭하면 같은 위치로 이동되버린다.
    // 라우터 사용법을 좀 더 공부해야한다. (라우터 기능의 개념 이해하기)
    return (
        <Router>
            <header>
                <h5>
                    <Link to="/">STOCKMAN</Link>
                </h5>
            </header>


            

                    <ul>
                        <li><Link to="/companylist">companyBoard</Link></li>
                    </ul>

                {/* 주소창의 경로와 매칭될 경우 보여줄 컴포넌트 할당 */}
                <Switch>
                    <Route path="/"  exact={true}><Home /></Route>
                    <Route path="/companylist"><CompanyBoard /></Route>
                    <Route path="*"><NotFound /></Route>
                </Switch>

        </Router>
    );
}