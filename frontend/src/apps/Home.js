import React, { useState }  from 'react';
import axios from 'axios';
import { useDispatch, useSelector, shallowEqual } from 'react-redux';
import '../CSS/Style.css';

import TitleBar from '../components/NavBar';
import CandleChart from '../components/Chart';
import FinancialTable from '../components/FinancialTable';
import PerformSearch from '../components/PerformSearch';
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
*/
export default function Home () {
    const [result, setResult] = useState(0);
    // 실적표, 조건검색표 가시, 비가시 상태 초기화
    const [finVisible, setFinVisible] = useState({visibility:'hidden', float: 'right'});
    const [perVisible, setPerVisible] = useState({visibility:'visible', float: 'right'});
    const [component, setComponent] = useState(false);

    // 리덕스 스토어로부터 검색정보 받기
    const { code, compName } = useSelector(
        state => ({
            code: state.searchReducer.code,
            compName: state.searchReducer.comp_name,
        }), shallowEqual);




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

    // 조건검색 전환 버튼 제어 함수
    /*
        1. 버튼 제어(클릭시 재무실적표 컴포넌트와 조건검색 컴포넌트 태그 교체 또는 비쥬블처리, 버튼도 조건검색, 재무실적표 버튼 교체처리)
        2. 
    */ 
    const changeComponent = (e) => {
        const btnState = e.target.value;

        switch (btnState) {
            case "조건검색":
                // 버튼 상태 처리 
                setFinVisible({visibility: 'visible', float: 'right'});
                setPerVisible({visibility: 'hidden'});
                setComponent(true);
                break;
            case "실적표" :
                setFinVisible({visibility: 'hidden', float: 'right'});
                setPerVisible({visibility: 'visible', float: 'right'});
                setComponent(false);
                break;
            default:
                setFinVisible({visibility: 'hidden', float: 'right'});
                setPerVisible({visibility: 'visible', float: 'right'});
                setComponent(false);
        }
    };
    
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

            <div className="container">
                <div className="row">
                    <div className="col-sm-12">
                        {/* 서브네비 */}
                        <h4 className="home-compname-text">{compName} {code}</h4>
                    </div>


                    <div className="col-sm-6 mx-auto">
                        {/* 차트 */}
                        <CandleChart />
                    </div>

                    <div className="col-sm-6 mx-auto">
                        {/* 재무,조건검색 */}
                        <div className="home-table-change-btn-div">
                            {/* 버튼을 누르면  조건검색 버튼 -> 재무실적 버튼, 재무실적 테이블 -> 조건검색 테이블*/}
                            <input type="button" name="componentChangeBtn" onClick={changeComponent} className="btn btn-primary" style={perVisible} value="조건검색"/>
                            <input type="button" name="componentChangeBtn" onClick={changeComponent} className="btn btn-primary" style={finVisible} value="실적표"/>
                        </div>
                        {component ? <FinSearchTable /> : <FinancialTable />}

                    </div>
                    <div className="col-sm-6 mx-auto">
                        {/* 뉴스사이트에서 해당 종목의 뉴스 헤드라인을 어떻게 끌어모아 표시할것인가 */}
                        {/* 뉴스/공시 */}
                    </div>
                    <div className="col-sm-6 mx-auto">
                        {/* 파이썬 로직 서버에 임의의 사용자 요청에 대한 응답을 어떻게 줄 것인가 */}
                        {/* 포트폴리오 */}

                        {/* 파이썬과 rest api를 이용해 간단한 통신해보기 */}
                        {/* 종목조건 검색 */}
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
                    <div className="col-sm-6 mx-auto">

                    </div>
                    <div className="col-sm-12">
                        <footer>
                            {/* 사이트의 작성자나 그에 따른 저작권 정보, 연락처 등을 명시한다. */}
                            <p>Copyright 2021. Morris all rights reserved</p>
                        </footer>
                    </div>
                </div>
            </div>
        </div>
    
    )

    // const [compsPosts, setCompPosts] = useState([]);
    // const [loading, setLoading] = useState(false);
    // const [error, setError] = useState(null);

    // // REST-API 서버에서 기업이름과 코드를 비동기로 받아오는 코드
    // const fetchComps = async() => {
    //     try {
    //         setError(null);
    //         setCompPosts(null);
    //         setLoading(true);

    //         const url = `http://localhost:8000/company_state/?page=1&data
    //         cache-control: max-age=60
    //         Cache-Control: no-store`; 
    //         const response = await axios.get(url);

    //         console.log(response.data.results.map(comps => {return comps.year}));
    //         // if (response.data.results.map(comps => {return comps.year}) === '2020'){
    //         //     console.log('ddd');
    //         // }

    //         setCompPosts(response.data.results);
    //     } catch(e) {
    //         setError(e);
    //     }
    //     setLoading(false);
    // };

    // useEffect(() => {
    //     fetchComps();
    // }, []);

    // if (loading) return <div>loading...</div>;
    // if (error) return <div>error.</div>;
    // if (!compsPosts) return null;

    // return (
    //     <div>
    //         <p>updated: 2021-05-23</p>
    //         <table className='table table-hover text-center'>
    //             <thead>
    //                 <tr>
    //                     <th>기업명</th>
    //                     <th>종목코드</th>
    //                     <th>시장</th>
    //                     <th>결산년도</th>
    //                     <th>시가총액</th>
    //                     <th>안정성</th>
    //                     <th>성장성</th>
    //                     <th>가치성</th>
    //                     <th>수익성</th>
    //                     <th>즐겨찾기</th>
    //                 </tr>
    //             </thead>
    //             <tbody>
    //             {compsPosts.map(comps => {
    //                 return (
    //                 <tr key={comps.code}> 
    //                     <td>{comps.company_nm}</td> 
    //                     <td>{comps.code}</td> 
    //                     <td>{comps.mk}</td>
    //                     <td>{comps.year}</td>
    //                     <td>150억</td>
    //                     <td>양호</td>
    //                     <td>양호</td>
    //                     <td>우수</td>
    //                     <td>위험</td>
    //                     <td>*</td>
    //                     </tr>);
    //             })}
    //             </tbody>
    //         </table>
    //     </div>
    // );
}