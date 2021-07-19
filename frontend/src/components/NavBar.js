import React from "react";
import axios from 'axios';
import { companyInfoActionObject } from '../modules/SearchReducer';
import { useDispatch } from 'react-redux';

// 리덕스를 사용해서 검색한 종목코드 또는 종목명 데이터를 넘겨야 겠다.
// 코스피, 코스닥, 금리, VIX 지수를 실시간 확인할수 있도록 기능을 넣어야한다.

/*
  1. 기본 검색 기능
  2. 검색어 미리보기 기능
  3. 최근 가격 표시
*/ 
export default function TitelBar () {
    const dispatch = useDispatch();

    const getCompanyInfo = async(e) => {
        try{
            e.preventDefault();  // 페이지 새로고침 막기
            const keyword = e.target.keyword.value;

            // keyword가 int인지 string 인지 분기 처리
            if (isNaN(keyword)) {
                // 종목명일 경우 (true)
                const url = `http://localhost:8000/api/company/?company=${keyword}`;
                const request = await axios.get(url);
                const code = request.data[0].code;
                

                // 리덕스 전달
                dispatch(companyInfoActionObject(code,keyword));
            }else {
                // 종목코드일 경우 (false)
                const url = `http://localhost:8000/api/company/?code=${keyword}`;
                const request = await axios.get(url);
                const comp_nm = request.data[0].company;

                // 리덕스 전달
                dispatch(companyInfoActionObject(keyword,comp_nm));
            }

        } catch (error) {
            // 검색이 되지 않았을 경우, 간단한 알림 띄우기(은은하게 떳다 사라지는게 좋을거 같음)
            
            console.error(error);
        }
    };

    return (
        <nav className="navbar navbar-expand navbar-dark bg-dark">
            <div className="container-fluid" >
                <a href="#home" className="navbar-brand">STOCKMAN</a>

                {/* search bar */}
                <ul className="navbar-nav me-auto mt-md-0 ">
                    <li className="nav-item hidden-sm-down">
                        <form className="app-search ps-3" onSubmit={getCompanyInfo}>
                            <input type="text" name='keyword' className="form-control" placeholder="종목검색"/> 
                                <a className="srh-btn">
                                    <i className="ti-search">
                                        {/* 검색 */}
                                    </i>
                                </a>
                        </form>
                    </li>
                </ul>

                <div className="me-auto navbar-nav">
                    {/* <a href="#home" data-rb-event-key="#home" className="nav-link active">Home</a>
                    <a href="#features" data-rb-event-key="#features" className="nav-link">Features</a>
                    <a href="#pricing" data-rb-event-key="#pricing" className="nav-link">Pricing</a> */}
                </div>
            </div>
        </nav>
    )

}