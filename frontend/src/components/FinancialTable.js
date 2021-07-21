import React, { useState, useEffect  }  from 'react';
import axios from 'axios';
import { useDispatch, useSelector, shallowEqual } from 'react-redux';

/*
    1. 좌우 연도 변경 버튼
    2. 연도, 수치 hover 표시
    3. 적자는 빨간색으로 표시
    4. 폰트 사이즈 조정 (테이블 사이즈 조정)
    5. 수치가 0 이거나 0.00일 경우 N/A 처리 하기
*/
export default function Tables () {
    const [finData, setFinData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // 종목코드 취득
    const { code, compName } = useSelector(
        state => ({
            code: state.searchReducer.code,
            compName: state.searchReducer.comp_name,
        }), shallowEqual);

        useEffect(() => {
            getFinYearData();
        }, [code]);


    /* 검색된 종목의 재무정보 취득 함수*/ 
    const getFinYearData = async() => {
        try {
            setError(null);
            setLoading(true);

            const url = `http://localhost:8000/api/company-state/?code=${code}`;
            const response = await axios.get(url);
            console.log(response.data);
            setFinData(response.data);
        } catch (error) {
            console.error(error);
        }
    };

    // 억단위 변환
    const moneyFormat = (money) => {
        if (isNA(money) !== "N/A"){
            // 마이너스면 붉은색으로 표시
            return Math.floor(money / 100000000).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        } else {
            return "N/A";
        }

    };

    // N/A 판별
    const isNA = (number) => {
        if (number === 0 || number === "0.00") {
            return "N/A";
        } else {
            return number;
        }
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

            <div className="table-change-table-div">
                {/* 버튼을 누르면 조건검색, 재무재표 버튼 체인지, 테이블 체인지 */}
                <button className="btn btn-primary">조건검색</button>
            </div>

            <table className="table table-hover">
            <thead>
                <tr className="active">
                    {/* 연도 */}
                    <th>실적</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{fin.year}</th>
                    })}

                </tr>
            </thead>
            
            <tbody>
                <tr>
                    <th>매출액(억원)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{moneyFormat(fin.revenue)}</th>
                    })}
                </tr>   

                <tr>
                    <th>매출총이익(억원)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{moneyFormat(fin.gross_profit)}</th>
                    })}
                </tr>   

                <tr>
                    <th>영업이익(억원)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{moneyFormat(fin.operating_profit)}</th>
                    })}
                </tr>   

                <tr>
                    <th>당기순이익(억원)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{moneyFormat(fin.net_profit)}</th>
                    })}
                </tr>   

                <tr>
                    <th>매출액증가율(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.sales_growth_rate)}</th>
                    })}
                </tr>   

                <tr>
                    <th>영업이익률(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.operating_margin)}</th>
                    })}
                </tr>   

                <tr>
                    <th>부채비율(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.debt_ratio)}</th>
                    })}
                </tr>   

                <tr>
                    <th>당좌비율(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.quick_ratio)}</th>
                    })}
                </tr>   

                <tr>
                    <th>유동비율(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.current_ratio)}</th>
                    })}
                </tr>   



                <tr>
                    <th>순이익증가율(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.net_profit_growth_rate)}</th>
                    })}
                </tr>   

                <tr>
                    <th>자산증가율(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.asset_growth_rate)}</th>
                    })}
                </tr>  

                <tr>
                    <th>PER(배)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.per)}</th>
                    })}
                </tr>   

                <tr>
                    <th>EPS(원)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.eps)}</th>
                    })}
                </tr>   

                <tr>
                    <th>PBR(배)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.pbr)}</th>
                    })}
                </tr>   

                <tr>
                    <th>BPS(원)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(Math.ceil(fin.bps))}</th>
                    })}
                </tr>   

                <tr>
                    <th>BIS(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.bis)}</th>
                    })}
                </tr>   

                <tr>
                    <th>ROA(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.roa)}</th>
                    })}
                </tr>   

                <tr>
                    <th>ROE(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.roe)}</th>
                    })}
                </tr>   

                <tr>
                    <th>자산회전율(%)</th>
                    {finData.map(fin => {
                        return <th key={fin.year}>{isNA(fin.asset_turnover)}</th>
                    })}
                </tr>

            </tbody>
        </table>
        </div>
        
    )
}