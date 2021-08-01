import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSelector, shallowEqual } from 'react-redux';

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
    const [deficit, setDeficit] = useState(); // 적자 체크
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
                        <th className="tooltip-graph" title="[수익성 지표] 최근 사업연도 50억 원 미만이면 관리종목 지정,
                        2년 연속이면 상장폐지(지주회사는 연결 기준), 코스닥은 30억원 미만">매출액(억)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.revenue < 5000000000 ? { color: "red" } : { color: "black" }}>
                                    {moneyFormat(fin.revenue)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[수익성 지표] 매출에서 최소한의 비용을 제거하여 남은 이익">매출총이익(억)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.gross_profit < 0 ? { color: "red" } : { color: "black" }}>
                                    {moneyFormat(fin.gross_profit)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[수익성 지표] 매출액에서 매출원가와 판매관리비등을 빼고 남은,
                        순수하게 영업을 통해서 창출된 이익">영업이익(억)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.operating_profit < 0 ? { color: "red" } : { color: "black" }}>
                                    {moneyFormat(fin.operating_profit)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[수익성 지표] 기업이 한해 동안 실제로 얻게 되는 순이익(IFRS 기준 우선)">당기순이익(억)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.net_profit < 0 ? { color: "red" } : { color: "black" }}>
                                    {moneyFormat(fin.net_profit)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[성장성 지표] 전년도 대비 금년도의 매출액의 증가 비율.
                        사업성 규모 성장등을 나타내므로 꾸준히 증가하는게 좋다">매출증가율(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.sales_growth_rate < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.sales_growth_rate)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[수익성 지표] 전년도 대비 금년도의 매출총이익의 증가 비율.
                        보통 40% 이상인 기업은 장기적인 경쟁우위를 가진 경우, 40%미만은 경쟁이 심한 업종에 속한 경우,
                        20% 미만은 장기적인 경쟁우위를 가질수 없을 정도로 경쟁이 극심한 업종에 속한 경우다. 동종업 비교에 활용하면 좋다.
                        5~10년간의 장기적인 추세 분석이 필요한 지표다">매출총이익률(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.gross_margin < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.gross_margin)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[수익성 지표] 매출액에서 발생한 영업수익에 대한 영업이익의 비율.
                        영업활동의 수익성, 판매마진을 나타낸다">영업이익률(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.operating_margin < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.operating_margin)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[안정성 지표] 기업이 가진 자산중에 부채가 어느 정도의 비중을 차지하는지를 나타내는 비율.
                        가령 부채비율이 150%라면 부채가 자본의 1.5배와 같다. 부채비율이 100%라면 자기자본과 부채가 같은 양이고,
                        100%이하라면 자기자본이 부채보다 많다는 의미다">부채비율(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.debt_ratio < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.debt_ratio)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[안정성 지표] 유동부채 대비 당좌자산의 비율로,
                        제품의 판매 없이 단기에 갚아야할 부채의 지급 능력과 기업의 유동성을 나타낸다.
                        일반적으로 당좌비율이 100%가 넘으면 안정적으로 현금조달을 할 수 있는 능력이 있다고 본다.
                        하지만 너무 높은 수치일 경우 쌓이는 현금을 효율적으로 재투자하지 못한다는 의미로 해석할수도 있기 때문에 이는 미래 수익성을 떨어뜨리는 요인이다">당좌비율(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.quick_ratio < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.quick_ratio)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[안정성 지표] 회사가 1년 안에 현금으로 바꿀 수 있는 유동자산을 1년 안에 갚아야할 유동부채로 나눈 값.
                        통상 유동비율이 150%~200%가 넘으면 기업의 재무 상태가 안정적이라고 평가할수 있다 (매출채권 조작 유의)">유동비율(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.current_ratio < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.current_ratio)}
                                </span>
                            </td>
                        })}
                    </tr>



                    <tr>
                        <th className="tooltip-graph" title="[성장성 지표] 전년도 대비 금년도의 당기순이익의 증가 비율.
                        사업의 수익성 규모가 얼마나 성장하고 있는가를 의미한다">당기순이익증가율(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.net_profit_growth_rate < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.net_profit_growth_rate)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[성장성 지표] 전년도 대비 금년도의 총자산 증가 비율.
                        기업의 전체적인 성장추세를 측정하는 지표. 매출액 증가율과 비교하여 기업의 과대투자 여부도 간접적으로 평가할수 있다">총자산증가율(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.asset_growth_rate < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.asset_growth_rate)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="주가수익률. 주가를 주당순이익으로 나눈것. 즉, 기업이 벌어들이는 이익에 비해 주가가 어느 정도인지를 가늠하는 지표. 동종업 기업들 기준, PER이 높다면 주당순이익에 비해 주식 가격이 높다는 것이고,
                        PER이 낮다면 주당순이익에 비해 주식 가격이 낮다는 것을 의미한다.
                        PER이 높다는것은 가격에 거품이 있다고도 볼 수도 있고, 주가가 높다는 것을 의미하며 그만큼 해당 종목에 투자자가 많이 몰려 있고 미래 수익에 대한 기대가 있다고도 볼 수 있으니 PER이 낮다고 해서 꼭 좋다고 할 순 없다. 영원히 저평가에 머물러 있는 기업들이 있기 때문이다. 따라서 절대적인 투자지표로 활용하기는 힘들다">PER(배)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.per < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.per)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[수익성 지표] 주당순이익. 당기순이익을 주식수로 나눈 값.
                        1 주당 1년동안 얼마나 돈을 벌어왔는지 알 수 있다. 따라서 EPS 자체가 높을수록 좋다.
                        하지만 주식수가 분모이기 때문에 당기순이익이 작아도 발행한 주식수가 적다면 EPS 수치는 커지고, 당기순이익이 커도 발행한 주식수가 많다면 EPS 수치는 작아진다. 따라서 절대적인 투자지표로 활용하기 힘들다">EPS(원)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.eps < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.eps).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[안정성 지표] 주가순자산배율. 주가를 주당 순자산으로 나눈 지표.
                        당시 주가가 주당 순자산의 몇 배로 거래되고 있는지를 보여준다. PBR이 1이라면 자본총계의 가치와 시장가치가 같다는 것을 의미한다.
                        PBR이 1 보다 작으면 주가보다 순자산 가치가 높다는 것을 의미한다. PBR은 기업의 순자산에 비해 주가가 적정하게 형성되었는지를 판단하는 지표다.
                        PER과 마찬가지로 높고 낮음의 기준은 따로 없기 때문에 동종업계와 비교가 필수다. 미래가치가 높은 종목들은 PBR 또한 높게 측정된 경우가 많다">PBR(배)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.pbr < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.pbr)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[안정성 지표] 주당순자산가치. 1 주당 순자산이 얼마인지를 알 수 있다.
                        총자산에서 총부채를 뺀 순자산을 시중에 발행된 주식 수로 나눈 값.
                        일종의 청산가치로 기업이 폐업을 해서 청산절차 이후에 1 주당 BPS만큼 주주들에게 배당을 해준다는 의미다.
                        따라서 BPS는 높을수록 좋다. (한계점: 재무상 정확하게 현실을 반영하고 있는지는 불확실)
                        ">BPS(원)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.bps < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(Math.ceil(fin.bps)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[안정성 지표] 자기자본율. 총자본주 자기자본이 차지하는 비중. 50%를 초과하면 자본이 부채보다 많은 상태고 그 미만이면 자본보다 부채가 더 많은 상태다.
                        통상적으로 자기자본이 부채총계보다 클 경우 재무적으로 안정되어 있다고 하므로, 자기자본비율이 50%에 가깝거나 그보다 높을수록 재무 안정성이 크다고 할 수 있다.
                        비율이 커질수록 재무건정성이 커진다는 것이므로 자본의 비중을 확인할 수 있다는 장점이 있다">BIS(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.bis < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.bis)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="총자산이익률. 자기자본에 부채까지 합친 차산 총액을 분모로 두고 계산.
                        은행대출로 낸 이익까지 고려하기 때문에, 대출까지 받았지만 동일한 이익을 낸 회사의 ROA는 더 적게 나타난다.
                        즉, 자기 자본이 거의 없는 기업이 과도하게 빚을 내서 투자한 경우 ROA에 반영되어 이를 판단할수 있는 지표다.
                        ROA에 비해 ROE가 현저하게 높다는 것은 기업이 가지고 있는 부채가 자기자본 대비 높다는 의미로 재무건전성을 의심해볼 필요가 있다">ROA(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.roa < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.roa)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="자기자본이익률. 기업이 자본을 이용해 얼마만큼의 이익을 냈는지 나타내는 지표.
                        투자자들이 투자한 금액 대비 이익을 얼만큼 내는지를 의미한다.
                        통상 ROE가 15% 이상으로 최근 3년 이내 꾸준히 증가 하는 기업일수록 좋다 (한계점: 은행 대출, 토지매각등으로 인해 창출된 이익은 반영 안됨).
                        ">ROE(%)</th>
                        {finData.map(fin => {
                            return <td className="text-center" key={fin.year}>
                                <span style={fin.roe < 0 ? { color: "red" } : { color: "black" }}>
                                    {isNA(fin.roe)}
                                </span>
                            </td>
                        })}
                    </tr>

                    <tr>
                        <th className="tooltip-graph" title="[활동성 지표] 매출활동을 함에 있어 기업의 보유자산을 몇번이나 활용했는지를 측정하는 비율.
                        총자산회전율이 높을수록 자산을 활용한 매출액이 높다고 할 수 있기 때문에 기업이 얼마나 효과적으로 자산을 잘 활용했는지 측정할 수 있는 지표이므로 높을수록 좋다">총자산회전율(%)</th>
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