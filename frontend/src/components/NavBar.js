import React from "react";
import axios from 'axios';
import { companyInfoActionObject } from '../modules/SearchReducer';
import { useDispatch } from 'react-redux';

// 리덕스를 사용해서 검색한 종목코드 또는 종목명 데이터를 넘겨야 겠다.
// 코스피, 코스닥, 금리, VIX 지수를 실시간 확인할수 있도록 기능을 넣어야한다.

/*
  1. 검색어 미리보기 기능 
     (종목 리스트를 모두 로드하고 정규식이든 뭐든 써서 사용자 타이핑을 감시하고 부분일치 리스트를 모두 보여주면 되지 않을까?)
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
                const url = `/api/company-state/?company_nm=${keyword}`;  // 배포용
                const request = await axios.get(url);
                const code = request.data[0].code;
                const sec_nm = request.data[0].sec_nm;

                // 리덕스 전달
                dispatch(companyInfoActionObject(code, keyword, sec_nm));
            }else {
                // 종목코드일 경우 (false)
                const url = `/api/company-state/?code=${keyword}`;  // 배포용
                const request = await axios.get(url);
                const comp_nm = request.data[0].company_nm;
                const sec_nm = request.data[0].sec_nm;

                // 리덕스 전달
                dispatch(companyInfoActionObject(keyword,comp_nm, sec_nm));
            }

        } catch (error) {
            // 검색이 되지 않았을 경우, 간단한 알림 띄우기(은은하게 떳다 사라지는게 좋을거 같음)
            console.error(error);
            return (
                alert('검색 결과가 없습니다.')
            );
        }
    };

    return (
        <nav className="navbar navbar-expand navbar-dark bg-dark">
            <div className="container-fluid" >
                <a href="#" className="navbar-brand">STOCKMAN</a>

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