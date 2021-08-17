import React, { useState } from 'react';
import '../CSS/Style.css';

import TitleBar from '../components/NavBar';
import CandleChart from '../components/Chart';
import FinancialTable from '../components/FinancialTable';
import FinSearchTable from '../components/FinSearchTable';

/*
  1. 종목조건 검색
  2. 포트폴리오 셀렉션
  3. 뉴스/공시 (크롤링?)
  4. 연간실적
  5. 동종업 실적 비교

  6. UI,CSS,레이아웃 조정
  7. 처음 보여줄 데이터 기준 정하기
  8. 최근 검색 항목 보여주기
  9. 현재 검색한 종목의 최근 종가 표시
  10. 코스피, 코스닥, 금리등의 정보 표시
  11. 적절한 위치에 업종 표시
  12. 검색창 개선하기
*/
export default function Home() {
    // 실적표, 조건검색표 가시, 비가시 상태 초기화
    const [btnState, setBtnState] = useState(false);  // 버튼 클릭 상태

    // 조건검색 전환 버튼 상태 객체
    const BtnStateObject = {
        btnValue: btnState ? "실적표" : "조건검색",
        btnStyle: {float: 'right'},
    };
    
    // // 계산 요청 메소드(POST)
    // const CalRequest = async(e) => {
    //     try {
    //         e.preventDefault();  // 페이지 새로고침 막기
    //         const RandomId = Math.random().toString(36).substr(2,11);

    //         const url = `/api/cal-request/`;

    //         await axios.post(url, {
    //             id: RandomId,
    //             operand_a: e.target.operand_a.value,
    //             operand_b: e.target.operand_b.value,
    //             operator: e.target.operator.value
    //         });

    //         GetResponse(RandomId);
    //         // DeleteResults(RandomId);

    //     } catch (error) {
    //         // 데이터를 전송하지 못한것에 대한 예외처리 필요
    //         console.error(error);
    //     };
    // };

    // // 계산된 값을 받는 메소드
    // const GetResponse = async(id) => {
    //     // 병렬처리 하기 위해선 로딩이 필요하다. 아니면 리스팅 시간을 없애던가, response 됐다는 신호가 필요하다. 
    //     try {
    //         const response = await axios.get(`/api/cal-response/?id=${id}`);
    //         setResult(response.data.results[0].return_val);

    //         // 처리된 response는 삭제(삭제하기전에 필요하다면 값 저장)
    //         await axios.delete(`/api/cal-response/${id}`); // delete 할 때는 쿼리스트링 형식은 404에러남
    //     } catch (error) {
    //         // 데이터를 읽지 못한 경우에 대한 예외처리 필요 (그럴 경우 현재 방식으로는 response에 값들이 남아 있게 된다.)
    //         console.error(error);
    //     }
    // };



    /* HTML */
    return (
        <div>
            {/* 네비를 라우터에 어떻게 동작하게 해야하나? 검색 기능 구현, 라우터에서 동작 설계 */}
            {/* fiexd position 적용 */}
            <div className="container-fluid">

                <div className="row">
                    <div className="col-sm-12">
                        <div className="nav-div">
                            <TitleBar />
                        </div>
                    </div>
                </div>

            </div>

            {/* 콘텐츠 레이아웃 */}
            <div className="container">
                <div className="row">

                    <div className="col-sm-12">
                        {/* 서브네비 */}
                        <div className="compinfo-text">
                            {/* 레이아웃 유지를 위한 공란 */}
                            <div>
                            </div>
                        </div>
                    </div>


                    <div className="col-sm-6 mx-auto">
                        {/* 차트 */}
                        <CandleChart />
                    </div>

                    <div className="col-sm-6 mx-auto" style={{ marginTop: "70px" }}>
                        {/* 재무,조건검색 */}
                        <div className="home-table-change-btn-div">
                            {/* 버튼을 누르면  조건검색 버튼 -> 재무실적 버튼, 재무실적 테이블 -> 조건검색 테이블*/}
                            <input type="button" onClick={() => setBtnState(!btnState)} className="btn btn-primary" style={BtnStateObject.btnStyle} value={BtnStateObject.btnValue} />
                        </div>

                        {btnState ? <FinSearchTable /> : <FinancialTable />}

                    </div>
                    <div className="col-sm-6 mx-auto">
                        {/* 뉴스사이트에서 해당 종목의 뉴스 헤드라인을 어떻게 끌어모아 표시할것인가 */}
                        {/* 뉴스/공시 */}
                    </div>
                    <div className="col-sm-6 mx-auto">
                        {/* 파이썬 로직 서버에 임의의 사용자 요청에 대한 응답을 어떻게 줄 것인가 */}

                        {/* 파이썬과 rest api를 이용해 간단한 통신해보기 */}
                        {/* <form onSubmit={CalRequest}>
                            <input name='operand_a' className='m-2' type='number' />
                            <input name='operand_b' type='number' /> */}

                        {/* <select name='operator'> */}
                        {/* input 에 입력한 숫자와 이 값들을 버튼을 클릭하면 CalRequest 함수로 보내야한다. */}
                        {/* <option type='text' value='add'>더하기</option>
                                <option type='text' value='sub'>빼기</option>
                                <option type='text' value='multi'>곱하기</option>
                                <option type='text' value='div'>나누기</option>
                            </select>

                            <input type='submit' id='cal' value='연산요청' />
                        </form> */}

                        {/* 결과값 */}
                        {/* <h2>{result}</h2> */}
                    </div>
                    <div className="col-sm-6 mx-auto">
                        {/* 동종업 실적 비교 */}
                    </div>
                </div>
            </div>

            {/* 푸터 */}
            <div className="container-fluid">

                <div className="row">
                    <div className="col-sm-12" style={{ padding: "0px" }}>
                        <footer
                            className="text-center text-lg-start text-white"
                            style={{ backgroundColor: "#3e4551" }}
                        >
                            {/* 텍스트 div */}
                            <div
                                className="text-center p-1"
                                style={{ backgroundColor: "rgba(1, 0, 0, 0.2)", width: "100%" }}
                            >
                                <p>Copyright 2021. Morris all rights reserved</p>
                            </div>

                        </footer>

                    </div>
                </div>
            </div>

        </div>

    );
}