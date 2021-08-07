import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSelector, shallowEqual } from 'react-redux';
import { IndicatorsObject } from './Tooltip';

/*
    1. 좌우 연도 변경 버튼
    2. 연도, 수치 hover 표시
    3. 적자는 빨간색으로 표시
    4. 폰트 사이즈 조정 (테이블 사이즈 조정)
    5. 수치가 0 이거나 0.00일 경우 N/A 처리 하기
*/
export default function Tables() {
    // component state
    const [finData, setFinData] = useState([]);
    const [finColorState, SetFinColorState] = useState();  // 적자는 붉은색으로 표시

    // 종목코드 취득
    const { code, compName } = useSelector(
        state => ({
            code: state.searchReducer.code,
            compName: state.searchReducer.comp_name,
        }), shallowEqual);

    useEffect(() => {
        getFinYearData();
    }, [code]);


    /* 검색된 종목의 재무정보 취득 함수:: Hook memo 사용 검토 */
    const getFinYearData = async () => {
        try {
            const url = `/api/company-state/?code=${code}`;  // 배포용
            const response = await axios.get(url);
            setFinData(response.data);
        } catch (error) {
            console.error(error);
        }
    };

    // 억 단위 변환
    const moneyFormat = (money) => {

        if (isNA(money) !== "N/A") {
            return Math.floor(money / 100000000).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        } else {
            return "N/A";
        }
    };

    // N/A 판별
    const isNA = (ratio) => {
        if (ratio === 0 || ratio === "0.00") {
            return "N/A";
        } else {
            return ratio;
        }
    };

    const tooltip = () => {
        return
    };

    /* 조건검색 테이블 변환 함수 */



    // if (loading) return <div>loading...</div>;
    // if (error) return <div>error.</div>;
    // if (!setFinData) return null;

    /* HTML */
    return (
        // 좌우 버튼을 두고 연도를 바꿀수 있게끔 만들어야 한다.

        <div className="table-div">
            <div className="table-btns-div">
                {/* <button className="btn btn-primary">이전</button>
            <button className="btn btn-primary">다음</button> */}
            </div>

            <table className="table table-bordered table-hover">
                <thead className="text-center">
                    <tr className="active">
                        {/* 연도 */}
                        <th>투자지표</th>
                        {finData.map(fin => {
                            return <th key={fin.year}>{fin.year}</th>
                        })}

                    </tr>
                </thead>

                <tbody>
                    <tr>
                        {/* 매출액 */}
                        {IndicatorsObject.revenue}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.revenue < 5000000000 ? { color: "red" } : { color: "black" }}>
                                    {moneyFormat(fin.revenue)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* 매출총이익 */}
                        {IndicatorsObject.gross_profit}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.gross_profit < 0 ? { color: "red" } : { color: "black" }}>
                                    {moneyFormat(fin.gross_profit)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* 영업이익 */}
                        {IndicatorsObject.operating_profit}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.operating_profit < 0 ? { color: "red" } : { color: "black" }}>
                                    {moneyFormat(fin.operating_profit)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* 당기순이익 */}
                        {IndicatorsObject.net_profit}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.net_profit < 0 ? { color: "red" } : { color: "black" }}>
                                    {moneyFormat(fin.net_profit)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* 매출액 증가율 */}
                        {IndicatorsObject.sales_growth_rate}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.sales_growth_rate < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.sales_growth_rate)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* 매출이익률 */}
                        {IndicatorsObject.gross_margin}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.gross_margin < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.gross_margin)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                       {/* 영업이익률 */}
                       {IndicatorsObject.operating_margin}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.operating_margin < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.operating_margin)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* 부채비율 */}
                        {IndicatorsObject.debt_ratio}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.debt_ratio < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.debt_ratio)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                         {/* 당좌비율 */}
                         {IndicatorsObject.quick_ratio}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.quick_ratio < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.quick_ratio)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* 유동비율 */}
                        {IndicatorsObject.current_ratio}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.current_ratio < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.current_ratio)}
                                </span>
                            </td>
                        })}
                    </tr>



                    <tr>
                        {/* 순이익증가율 */}
                        {IndicatorsObject.net_profit_growth_rate}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.net_profit_growth_rate < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.net_profit_growth_rate)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* 총자산증가율 */}
                        {IndicatorsObject.asset_growth_rate}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.asset_growth_rate < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.asset_growth_rate)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                       {/* PER */}
                       {IndicatorsObject.PER}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.per < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.per)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                       {/* EPS */}
                       {IndicatorsObject.EPS}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.eps < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.eps).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* PBR */}
                        {IndicatorsObject.PBR}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.pbr < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.pbr)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* BPS */}
                        {IndicatorsObject.BPS}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.bps < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(Math.ceil(fin.bps)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                       {/* BIS */}
                       {IndicatorsObject.BIS}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.bis < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.bis)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                       {/* ROA */}
                       {IndicatorsObject.ROA}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.roa < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.roa)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        {/* ROE */}
                        {IndicatorsObject.ROE}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.roe < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.roe)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                         {/* 자산회전율 */}
                         {IndicatorsObject.asset_turnover}
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.asset_turnover < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.asset_turnover)}
                                </span>
                            </td>
                        })}
                    </tr>

                </tbody>
            </table>
        </div>

    )
}