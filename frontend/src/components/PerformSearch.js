/* 조건검색 */
import React, { useState, useEffect  }  from 'react';
import axios from 'axios';
import { useDispatch, useSelector, shallowEqual } from 'react-redux';


/*
    1. 조건 입력 아이템 추가, 삭제
    2. 셀렉트 옵션 설정 (옵션 중복을 어떻게 제외시키지?)
    3. url, quearyString 조합하기
    4. 연도는 무조건 최근 연도
*/
export default function PerformSearch () {
    /* JS */
    const createConditionItem = () => {
        const options = new Array("")
    }

    /* HTML */
    return (
        // 검색버튼을 누르면 조건입력창과 검색버튼은 hidden 상태,
        <div className="per-input-box-div">
            <input className="btn btn-outline-primary" type='button' value='검색' />
            <input className="btn btn-outline-primary" type='button' value='조건추가' />

            <table className="table">
                <thead>

                    <tr>
                        <th>지표</th>
                    </tr>

                </thead>

                <tbody>

                    <tr>
                        <div>
                        <select>
                            <option>PER</option>
                            <option>BIS</option>
                        </select>

                        <input type="text"  placeholder="최소"/>
                        ~
                        <input type="text" placeholder="최대"/>
                        <input type="button" className="btn btn-default btn-sm" value="삭제"/>
                        </div>

                    </tr>

                    <tr>
                    </tr>

                </tbody>
            </table>
        </div>
    )
}