import React, { useState, useEffect  }  from 'react';
import axios from 'axios';
import { useDispatch, useSelector, shallowEqual } from 'react-redux';

export default function FinSearchTable () {
    return (
        <div className="table-div">

            {/* <div className="table-btns-div">
                <button className="btn btn-primary">검색</button>
            </div> */}

            <table className="table table-bordered table-hover">
                <thead className="text-center">
                    <tr className="">
                        <th><button className="btn btn-outline-primary btn-sm">검색</button></th>
                        <th>최소</th>
                        <th>최대</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <th>매출액(억원)</th>
                        <th><input type="number" /></th>
                        <th><input type="number" /></th>

                    </tr>

                    <tr>
                        <th>매출총이익(억원)</th>

                    </tr>

                    <tr>
                        <th>영업이익(억원)</th>

                    </tr>

                    <tr>
                        <th>당기순이익(억원)</th>

                    </tr>

                    <tr>
                        <th>매출액증가율(%)</th>

                    </tr>

                    <tr>
                        <th>영업이익률(%)</th>

                    </tr>

                    <tr>
                        <th>부채비율(%)</th>

                    </tr>

                    <tr>
                        <th>당좌비율(%)</th>

                    </tr>

                    <tr>
                        <th>유동비율(%)</th>

                    </tr>



                    <tr>
                        <th>순이익증가율(%)</th>

                    </tr>

                    <tr>
                        <th>자산증가율(%)</th>

                    </tr>

                    <tr>
                        <th>PER(배)</th>

                    </tr>

                    <tr>
                        <th>EPS(원)</th>

                    </tr>

                    <tr>
                        <th>PBR(배)</th>

                    </tr>

                    <tr>
                        <th>BPS(원)</th>

                    </tr>

                    <tr>
                        <th>BIS(%)</th>

                    </tr>

                    <tr>
                        <th>ROA(%)</th>

                    </tr>

                    <tr>
                        <th>ROE(%)</th>
                    </tr>

                    <tr>
                        <th>자산회전율(%)</th>

                    </tr>

                </tbody>
            </table>
        </div>
    )
}