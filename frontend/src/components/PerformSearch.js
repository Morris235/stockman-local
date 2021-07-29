/* 조건검색 */
import React, { useState, useEffect  }  from 'react';
import axios from 'axios';
import { useDispatch, useSelector, shallowEqual } from 'react-redux';
import LinkedList from './LinkedList';


/*
    1. 조건 입력 아이템 추가, 삭제
    2. 셀렉트 옵션 설정 (옵션 중복을 어떻게 제외시키지?)
    3. url, quearyString 조합하기
    4. 연도는 무조건 최근 연도, 최근 연도라는걸 안내 문구 표시
*/
export default function PerformSearch () {
    /* JS */
    // 상태
    let [indexNum, setIndexNum] = useState(0);
    let [itemArr, setItemArr] = useState([]);

    const rootUrl = `http://localhost:8000/api/company-state/`;  // 개발용
    // const rootUrl = `/api/company-state/`;  // 배포용
    let linkedList = new LinkedList();

    // linkedList.append("hello");
    // linkedList.append("LinkedList");
    // linkedList.insert("A", "head"); // head 추가, 맨 앞으로 데이터를 추가함
    // linkedList.insert("B", "A");
    // linkedList.insert("C", "B");
    // linkedList.remove("B");
    // linkedList.append("D");
    // linkedList.append("E");

    // 각 수치 입력폼 함수
    const conditionItem = () => {
        const options = [
            "매출액", "매출총이익", "영업이익", "당기순이익", "매출액증가율",
            "영업이익률", "부채비율", "당좌비율", "유동비율", "순이익증가율", "자산증가율",
            "PER", "EPS", "PBR", "BPS", "BIS", "ROA",
            "ROE", "자산회전율"];

        /*
        매핑 예시
            {finData.map(fin => {
                return <td key={fin.year}>{moneyFormat(fin.revenue)}</td>
            })}
        */

        // 맵핑? 위치는 어떻게 지정하지?
        // 만들수 있는 최대 개수 = 각 지표 개수 + 종가
        // set은 중복값을 허용하지 않는다. 이를 활용하여 아이템이 추가되더라도 같은 조건을 선택할수 없도록 강제한다.
        const Item = 
            <div>
                <select>
                    {/* 옵션 매핑 */}
                    {options.map(opt => {
                        return <option>{opt}</option>
                    })}
                </select>
                {/* 매출액, 매출총이익, 영업이익, 당기순이익은 억원으로 환산 안내 */}
                <input type="number" placeholder="최소" />
                ~
                <input type="number" placeholder="최대" />
                <input id='deleteBtn' type="button" className="btn btn-default btn-sm" onClick={onClickConditionDelete} value="삭제" />
            </div>;

        return Item;
    };


    // doc에 조건 아이템을 추가
    const onClickConditionAdd = () => {
        // linked list를 사용해서 아이템을 추가 삭제하기 : 데이터를 중간에 삭제하거나 추가하기가 용이하다. 대신 구현이 어려움

        // 조건 추가 제한 20개 (지표+종가)
        if (itemArr.length < 5){
            // itemArr[indexNum] = conditionItem();
            // setIndexNum(indexNum+1);
            // setItemArr(itemArr);

            linkedList.append(conditionItem());
            setItemArr(linkedList.element());
            // alert(linkedList.element());
        }
    };

    // doc에 조건 아이템 삭제
    const onClickConditionDelete = () => {
        // 조건 무조건 한 개는 남겨두기
        // 위치를 어떻게 알수 있지?
        delete itemArr[1];
        console.log(itemArr);
    };

    // 선택한 옵션을 rootUrl과 join하여 쿼리스트링을 만들고 쿼리하여 조건에 맞는 기업리스트를 받아 온다.
    const onSearchConditons = () => {
        // select에서 선택한 옵션들을 캐치하는 장치 필요
        // 해시 테이블로 각 옵션과 쿼리 스트링을 짝짓는다.
    };

    // 조건 테이블
    const ConditionTable = () => {
        const table = <div>
            {itemArr.map(item => {
                return item
            })}
            </div>;

        // const table = 
        // <div>
        //     {linkedList.map(item => {
        //         return item.element()
        //     })}
        // </div>;

        return table;
    };

    /* HTML */
    return (
        // 검색버튼을 누르면 조건입력창과 검색버튼은 hidden 상태,
        <div className="per-input-box-div">
            <input className="btn btn-outline-primary" type='button' value='검색' />
            <input className="btn btn-outline-primary" type='button' onClick={onClickConditionAdd} value='조건추가' />

            <table className="table-responsive-md" name="conditionTable">
                <thead>

                    <tr>
                        <th>지표</th>
                    </tr>

                </thead>
                {/* tbody에 스크롤이 필요하다. */}
                <tbody>

                    <tr>
                        {/* 이 div의 id를 지정해서 이 안에 아이템이 생기게 만들어야 한다. */}
                        {/* <div>
                            {itemArr.map(item => {
                                return item
                            })}
                        </div> */}
                        {ConditionTable()}

                    </tr>

                </tbody>
            </table>
        </div>
    )
}