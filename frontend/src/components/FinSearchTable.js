import React, { useState } from 'react';
import axios from 'axios';
import { useDispatch } from 'react-redux';
import { companyInfoActionObject } from '../modules/SearchReducer';
import { IndicatorsObject } from './Tooltip';

/*
    1. 검색 결과를 resultHTML로 넘기기 (상태를 이용?) : 완료
    2. conditionHTML과 resultHTML간의 스위칭 구조 구현
    3. resultHTML 디자인 하기 
    4. 주소창에 쿼리스트링이 표시되는 문제 파악하고 해결하기
    5. 종목을 클릭하면 해당 종목을 검색, 주가차트 표시
*/
export default function FinSearchTable() {
    // 조건검사 결과 데이터
    const [resultData, setResultData] = useState();
    const [changeResultHTML, setChangeResultHTML] = useState(false);  // 결과 테이블 HTML 출력
    const [conditionArr, setConditionArr] = useState();  // 입력한 조건들만 저장하는 변수

    const dispatch = useDispatch();
    // rootQuery
    // const rootQueryString = `http://localhost:8000/api/company-state/`;  // 개발용
    const rootQueryString = `/api/company-state/`  // 배포용


    // conditionHTML의 form의 input값들을 쿼리스트링으로 변환및 결과값을 set하는 함수
    const handleForm = async (e) => {
        try {
            // 조건검색 쿼리 : 무식하게 코딩함. 유지보수가 더 쉽고 효율적인 코드로 바꿔야함
            const data = new FormData(e.target);

            // 입력한 정보만 쿼리를 하는게 필요하다. 이런식으로 쿼리를 하면 성능이 떨어질수 있다. 
            const finQueryStr = `${rootQueryString}?year=2020
            &min_revenue=${data.get('min_revenue').length === 0 ? '' : data.get('min_revenue') * 100000000}
            &max_revenue=${data.get('max_revenue').length === 0 ? '' : data.get('max_revenue') * 100000000}
            &min_gross_profit=${data.get('min_gross_profit').length === 0 ? '' : data.get('min_gross_profit') * 100000000}
            &max_gross_profit=${data.get('max_gross_profit').length === 0 ? '' : data.get('max_gross_profit') * 100000000}
            &min_operating_profit=${data.get('min_operating_profit').length === 0 ? '' : data.get('min_operating_profit') * 100000000}
            &max_operating_profit=${data.get('max_operating_profit').length === 0 ? '' : data.get('max_operating_profit') * 100000000}
            &min_net_profit=${data.get('min_net_profit').length === 0 ? '' : data.get('min_net_profit') * 100000000}
            &max_net_profit=${data.get('max_net_profit').length === 0 ? '' : data.get('max_net_profit') * 100000000}
            &min_sales_growth_rate=${data.get('min_sales_growth_rate')}&max_sales_growth_rate=${data.get('max_sales_growth_rate')}
            &min_gross_margin=${data.get('min_gross_margin')}&max_gross_margin=${data.get('max_gross_margin')}
            &min_operating_margin=${data.get('min_operating_margin')}&max_operating_margin=${data.get('max_operating_margin')}
            &min_debt_ratio=${data.get('min_debt_ratio')}&max_debt_ratio=${data.get('max_debt_ratio')}
            &min_quick_ratio=${data.get('min_quick_ratio')}&max_quick_ratio=${data.get('max_quick_ratio')}
            &min_current_ratio=${data.get('min_current_ratio')}&max_current_ratio=${data.get('max_current_ratio')}
            &min_net_profit_growth_rate=${data.get('min_net_profit_growth_rate')}&max_net_profit_growth_rate=${data.get('max_net_profit_growth_rate')}
            &min_asset_growth_rate=${data.get('min_asset_growth_rate')}&max_asset_growth_rate=${data.get('max_asset_growth_rate')}
            &min_per=${data.get('min_per')}&max_per=${data.get('max_per')}
            &min_eps=${data.get('min_eps')}&max_eps=${data.get('max_eps')}
            &min_pbr=${data.get('min_pbr')}&max_pbr=${data.get('max_pbr')}
            &min_bps=${data.get('min_bps')}&max_bps=${data.get('max_bps')}
            &min_bis=${data.get('min_bis')}&max_bis=${data.get('max_bis')}
            &min_roa=${data.get('min_roa')}&max_roa=${data.get('max_roa')}
            &min_roe=${data.get('min_roe')}&max_roe=${data.get('max_roe')}
            &min_asset_turnover=${data.get('min_asset_turnover')}
            &max_asset_turnover=${data.get('max_asset_turnover')}`;

            // 가격(종가) 검색 쿼리: 조건 검색되어 나온 기업명, 종목코드와 가격조건에 검색된 기업명과 종목코드를 대조하여 일치하는 기업명만 표시하면 가격조건도 포함시킬수 있다.
            const priceQueryStr = ``;

            const response = await axios.get(finQueryStr.replace(/(\s*)/g, ""));  // 공백문자 제거

            // 결과값을 상태 저장
            setResultData(response.data);
            console.log(response.data);

            // 결과값을 모두 받아오면 ResultHTML로 상태 변경
            setChangeResultHTML(true);
        } catch (error) {
            console.error(error);
        }

    };

    // 재검색 버튼 클릭 컴포넌트 로컬 상태 변화 함수
    const onClickedStateChange = () => {
        setChangeResultHTML(false);
    };

    /* 조건검색 form HTML */
    const conditionHTML = () => {
        /*
            1.기존에 검색한 수치를 각 입력 폼에 그대로 두기 (리덕스 스토어로 구현 가능할듯 함)
        */
        return (
            <div>
                (2020년 기준)
                <form name="conditions" id="conditions" onSubmit={e => {
                    e.preventDefault();
                    handleForm(e);
                }}>

                    <input type="hidden" name="year" value="2020" />
                    <table className="table table-bordered table-hover">

                        <thead className="text-center">
                            <tr>
                                {/* 검색버튼을 누르거나 엔터로 검색을 하면 resultHTML을 표시하도록 제어한다. */}
                                <th><button className="btn btn-outline-primary btn-sm" type="submit">검색</button></th>
                                <th>최소</th>
                                <th>최대</th>
                            </tr>
                        </thead>

                        <tbody className="text-center">
                            <tr>
                                {/* 매출액 */}
                                {IndicatorsObject.revenue}
                                <th><input type="number" name="min_revenue" /></th>
                                <th><input type="number" name="max_revenue" /></th>
                            </tr>

                            <tr>
                                {/* 매출총이익 */}
                                {IndicatorsObject.gross_profit}
                                <th><input type="number" name="min_gross_profit" /></th>
                                <th><input type="number" name="max_gross_profit" /></th>
                            </tr>

                            <tr>
                                {/* 영업이익 */}
                                {IndicatorsObject.operating_profit}
                                <th><input type="number" name="min_operating_profit" /></th>
                                <th><input type="number" name="max_operating_profit" /></th>
                            </tr>

                            <tr>
                                {/* 당기순이익 */}
                                {IndicatorsObject.net_profit}
                                <th><input type="number" name="min_net_profit" /></th>
                                <th><input type="number" name="max_net_profit" /></th>
                            </tr>

                            <tr>
                                {/* 매출액 증가율 */}
                                {IndicatorsObject.sales_growth_rate}
                                <th><input type="number" name="min_sales_growth_rate" /></th>
                                <th><input type="number" name="max_sales_growth_rate" /></th>
                            </tr>

                            <tr>
                                {/* 매출이익률 */}
                                {IndicatorsObject.gross_margin}
                                <th><input type="number" name="min_gross_margin" /></th>
                                <th><input type="number" name="max_gross_margin" /></th>
                            </tr>

                            <tr>
                                {/* 영업이익률 */}
                                {IndicatorsObject.operating_margin}
                                <th><input type="number" name="min_operating_margin" /></th>
                                <th><input type="number" name="max_operating_margin" /></th>
                            </tr>

                            <tr>
                                {/* 부채비율 */}
                                {IndicatorsObject.debt_ratio}
                                <th><input type="number" name="min_debt_ratio" /></th>
                                <th><input type="number" name="max_debt_ratio" /></th>
                            </tr>

                            <tr>
                                {/* 당좌비율 */}
                                {IndicatorsObject.quick_ratio}
                                <th><input type="number" name="min_quick_ratio" /></th>
                                <th><input type="number" name="max_quick_ratio" /></th>
                            </tr>

                            <tr>
                                {/* 유동비율 */}
                                {IndicatorsObject.current_ratio}
                                <th><input type="number" name="min_current_ratio" /></th>
                                <th><input type="number" name="max_current_ratio" /></th>
                            </tr>

                            <tr>
                                {/* 순이익증가율 */}
                                {IndicatorsObject.net_profit_growth_rate}
                                <th><input type="number" name="min_net_profit_growth_rate" /></th>
                                <th><input type="number" name="max_net_profit_growth_rate" /></th>
                            </tr>

                            <tr>
                                {/* 총자산증가율 */}
                                {IndicatorsObject.asset_growth_rate}
                                <th><input type="number" name="min_asset_growth_rate" /></th>
                                <th><input type="number" name="max_asset_growth_rate" /></th>
                            </tr>

                            <tr>
                                {/* PER */}
                                {IndicatorsObject.PER}
                                <th><input type="number" name="min_per" /></th>
                                <th><input type="number" name="max_per" /></th>
                            </tr>

                            <tr>
                                {/* EPS */}
                                {IndicatorsObject.EPS}
                                <th><input type="number" name="min_eps" /></th>
                                <th><input type="number" name="max_eps" /></th>
                            </tr>

                            <tr>
                                {/* PBR */}
                                {IndicatorsObject.PBR}
                                <th><input type="number" name="min_pbr" /></th>
                                <th><input type="number" name="max_pbr" /></th>
                            </tr>

                            <tr>
                                {/* BPS */}
                                {IndicatorsObject.BPS}
                                <th><input type="number" name="min_bps" /></th>
                                <th><input type="number" name="max_bps" /></th>
                            </tr>

                            <tr>
                                {/* BIS */}
                                {IndicatorsObject.BIS}
                                <th><input type="number" name="min_bis" /></th>
                                <th><input type="number" name="max_bis" /></th>
                            </tr>

                            <tr>
                                {/* ROA */}
                                {IndicatorsObject.ROA}
                                <th><input type="number" name="min_roa" /></th>
                                <th><input type="number" name="max_roa" /></th>
                            </tr>

                            <tr>
                                {/* ROE */}
                                {IndicatorsObject.ROE}
                                <th><input type="number" name="min_roe" /></th>
                                <th><input type="number" name="max_roe" /></th>
                            </tr>

                            <tr>
                                {/* 자산회전율 */}
                                {IndicatorsObject.asset_turnover}
                                <th><input type="number" name="min_asset_turnover" /></th>
                                <th><input type="number" name="max_asset_turnover" /></th>
                            </tr>

                        </tbody>
                    </table>
                </form>
            </div>
        );
    };


    /* 검색된 결과를 표시하는 HTML */
    const resultHTML = () => {
        /*
            1.스크롤이 가능한 테이블이여야 한다. 또는 테이블과 비슷한 구조여야 한다.
            2.재검색 버튼 만들기: 클릭하면 다시 conditionHTML로 넘어간다.
            3.입력한 조건의 지표들만 표시
            4.결과가 없을경우의 화면 표시
            5.실적표 버튼을 누르고 다시 기존 검색한 종목들을 볼수 있도록 검색결과 화면으로 돌아올수 있게 하기 (리덕스 스토어로 구현 가능할듯 함)
        */

        if (resultData.length > 0) {
            return (
                <div className="fixed-table-container">
                    {/* 연도 기준을 최신 연도로 할지 아니면 사용자가 선택하게 할지 
                    아니면 조건검색의 근본 개념을 각 투자지표들의 지속성을 평가하는걸로 바꿔서 연도 기준 자체를 없앨지 정해야함 */}
                    (2020년 기준)
                    <div className="fixed-table-body">
                        <table className="table table-bordered table-hover table-responsive-md">
                            <thead className="text-center">
                                <tr>
                                    <th scope="col"><button className="btn btn-outline-primary btn-sm" onClick={onClickedStateChange}>재검색</button></th>
                                    <th scope="col">종목명 ({resultData.length}개)</th>
                                    {/* 입력한 조건의 투자지표만 표시? */}
                                    {/* <th>지표</th> */}
                                </tr>
                            </thead>

                            <tbody className="text-center">
                                {resultData.map(data => {
                                    return (
                                        // 클릭시 해당 종목 검색
                                        <tr className="trow" key={data.code} tyep="button" onClick={() => { dispatch(companyInfoActionObject(data.code, data.company_nm, data.sec_nm, data.mk)); }}>
                                            <th>{/* 실적보기 버튼 만들어서 관련종목의 검색한 연도의 실적표를 팝업으로 띄우기 */}</th>
                                            <td>
                                                <div>
                                                    <b>{data.company_nm}</b>
                                                </div>
                                                <div>
                                                    [{data.sec_nm}]
                                                </div>

                                            </td>
                                            {/* 입력한 조건의 투자지표만 표시 */}
                                            {/* <td>
                                                {data.current_ratio}
                                            </td> */}
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            );
        }

        /* 결과값 없음 */
        else {
            return (
                <div>
                    <div className="fixed-table-body">
                        <table className="table table-bordered table-hover">
                            <thead className="text-center">
                                <tr>
                                    <th><button className="btn btn-outline-primary" onClick={onClickedStateChange}>재검색</button></th>
                                </tr>
                            </thead>

                            <tbody className="text-center">
                                <tr>
                                    <th>
                                        조건에 맞는 검색 결과가 없습니다.
                                    </th>

                                </tr>

                            </tbody>
                        </table>
                    </div>
                </div>
            );
        }

    };


    /* HTML */
    return (
        <div className="table-div">
            {/* 테이블 전체를 jsx 방식으로 대체한다. */}
            {changeResultHTML ? resultHTML() : conditionHTML()}
        </div>
    )
}