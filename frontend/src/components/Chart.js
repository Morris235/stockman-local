import React, { useEffect, useRef, useState } from 'react';
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";
import { useSelector, shallowEqual } from 'react-redux';
import axios from 'axios';

/*
  1. 디스포즈 구현 (DOM 제어 에러 발생)
  2. 성능 최적화 (느림)
  3. UI 꾸미기 (버튼, from, to input 상자, 캔들 색상)
  4. 수정주가 계산및 구현
  5. 이동평균선, MACD, 추세선등등 기능 확장
*/

export default function Charts() {
  const chart = useRef(null);
  // 현재 선택한 종목의 종가
  const [closePrice, setClosePrice] = useState();
  const [lastUpdatePrice, setLastUpdatePrice] = useState();
  const [sec, setSec] = useState();
  // useRef

  // 종목코드 상태 참조
  const { code, compName, sec_nm } = useSelector(
    state => ({
      code: state.searchReducer.code,
      compName: state.searchReducer.comp_name,
      sec_nm: state.searchReducer.sec_nm,
    }), shallowEqual);

  // 라이프 사이클을 고려하지 않으면 새로고침할때 2개의 차트가 생겨버린다. 
  // 따라서 코딩 당시 판단으로 useEffect에 차트 코드를 넣을수 밖에 없었음
  useEffect(() => {
    // CandleChart();
    getPrice();
    /* Chart code */
    // Themes begin
    am4core.useTheme(am4themes_animated);
    //Themes end

    // Create chart 
    let x = am4core.create("chartdiv", am4charts.XYChart);
    x.padding(0, 15, 0, 15);

    /* 데이터를 취득하지 못했던 이유: 
       1. 쿼리스트링 오타 => code를 id로 표시함
       2. 백엔드에서 페이징을 걸어버려서 JSON 형식이 amcharts4가 읽지 못하는 형식이 되버림
    */
    x.dataSource.url = `/api/daily-price/?code=${code}`;  // 배포용

    x.dataSource.parser = new am4core.JSONParser();
    x.dataSource.parser.options.emptyAs = 0;

    x.dataSource.parser.options.useColumnNames = true;
    x.dataSource.parser.options.reverse = true;

    // the following line makes value axes to be arranged vertically.
    x.leftAxesContainer.layout = "vertical";


    // 여기서부터 라이브러리의 빠른 테스트를 위해 복붙함
    // uncomment this line if you want to change order of axes
    //chart.bottomAxesContainer.reverseOrder = true;

    let dateAxis = x.xAxes.push(new am4charts.DateAxis());
    dateAxis.renderer.grid.template.location = 0;
    dateAxis.renderer.ticks.template.length = 8;
    dateAxis.renderer.ticks.template.strokeOpacity = 0.1;
    dateAxis.renderer.grid.template.disabled = true;
    dateAxis.renderer.ticks.template.disabled = false;
    dateAxis.renderer.ticks.template.strokeOpacity = 0.2;
    dateAxis.renderer.minLabelPosition = 0.01;
    dateAxis.renderer.maxLabelPosition = 0.99;
    dateAxis.keepSelection = true;
    dateAxis.minHeight = 30;

    dateAxis.groupData = true;
    dateAxis.minZoomCount = 5;

    // these two lines makes the axis to be initially zoomed-in
    // dateAxis.start = 0.7;
    // dateAxis.keepSelection = true;

    let valueAxis = x.yAxes.push(new am4charts.ValueAxis());
    valueAxis.tooltip.disabled = true;
    valueAxis.zIndex = 1;
    valueAxis.renderer.baseGrid.disabled = true;
    // height of axis
    valueAxis.height = am4core.percent(65);

    valueAxis.renderer.gridContainer.background.fill = am4core.color("#000000");
    valueAxis.renderer.gridContainer.background.fillOpacity = 0.05;
    valueAxis.renderer.inside = true;
    valueAxis.renderer.labels.template.verticalCenter = "bottom";
    valueAxis.renderer.labels.template.padding(1, 1, 1, 1);

    //valueAxis.renderer.maxLabelPosition = 0.95;
    valueAxis.renderer.fontSize = "0.8em"

    let series = x.series.push(new am4charts.CandlestickSeries());
    series.dataFields.dateX = "date";
    series.dataFields.openValueY = "open";
    series.dataFields.valueY = "close";
    series.dataFields.lowValueY = "low";
    series.dataFields.highValueY = "high";
    series.clustered = false;
    series.tooltipText = "open: {openValueY.value}\nlow: {lowValueY.value}\nhigh: {highValueY.value}\nclose: {valueY.value}";
    series.name = "JSON";
    series.defaultState.transitionDuration = 0;


    let valueAxis2 = x.yAxes.push(new am4charts.ValueAxis());
    valueAxis2.tooltip.disabled = true;
    // height of axis
    valueAxis2.height = am4core.percent(35);
    valueAxis2.zIndex = 3
    // this makes gap between panels
    valueAxis2.marginTop = 30;
    valueAxis2.renderer.baseGrid.disabled = true;
    valueAxis2.renderer.inside = true;
    valueAxis2.renderer.labels.template.verticalCenter = "bottom";
    valueAxis2.renderer.labels.template.padding(2, 2, 2, 2);
    //valueAxis.renderer.maxLabelPosition = 0.95;
    valueAxis2.renderer.fontSize = "0.8em"

    valueAxis2.renderer.gridContainer.background.fill = am4core.color("#000000");
    valueAxis2.renderer.gridContainer.background.fillOpacity = 0.05;

    let series2 = x.series.push(new am4charts.ColumnSeries());
    series2.dataFields.dateX = "date";
    series2.clustered = false;
    series2.dataFields.valueY = "volume";
    series2.yAxis = valueAxis2;
    series2.tooltipText = "{valueY.value}";
    series2.name = "Series 2";
    // volume should be summed
    series2.groupFields.valueY = "sum";
    series2.defaultState.transitionDuration = 0;

    x.cursor = new am4charts.XYCursor();

    let scrollbarX = new am4charts.XYChartScrollbar();

    let sbSeries = x.series.push(new am4charts.LineSeries());
    sbSeries.dataFields.valueY = "close";
    sbSeries.dataFields.dateX = "date";
    scrollbarX.series.push(sbSeries);
    sbSeries.disabled = true;
    scrollbarX.marginBottom = 20;
    x.scrollbarX = scrollbarX;
    scrollbarX.scrollbarChart.xAxes.getIndex(0).minHeight = undefined;



    /**
     * Set up external controls
     */

    // Date format to be used in input fields
    let inputFieldFormat = "yyyy-MM-dd";

    // dispose후에 버튼을 제어할려고 하니까 에러가 발생한다. document를 직접 제어하는 방법 말고 다른 방법을 써야 한다.
    // document.getElementById("b1m").addEventListener("click", function () {
    //   let max = dateAxis.groupMax["day1"];
    //   let date = new Date(max);
    //   am4core.time.add(date, "month", -1);
    //   zoomToDates(date);
    // });

    // document.getElementById("b3m").addEventListener("click", function () {
    //   let max = dateAxis.groupMax["day1"];
    //   let date = new Date(max);
    //   am4core.time.add(date, "month", -3);
    //   zoomToDates(date);
    // });

    // document.getElementById("b6m").addEventListener("click", function () {
    //   let max = dateAxis.groupMax["day1"];
    //   let date = new Date(max);
    //   am4core.time.add(date, "month", -6);
    //   zoomToDates(date);
    // });

    // document.getElementById("b1y").addEventListener("click", function () {
    //   let max = dateAxis.groupMax["day1"];
    //   let date = new Date(max);
    //   am4core.time.add(date, "year", -1);
    //   zoomToDates(date);
    // });

    // document.getElementById("bytd").addEventListener("click", function () {
    //   let max = dateAxis.groupMax["day1"];
    //   let date = new Date(max);
    //   am4core.time.round(date, "year", 1);
    //   zoomToDates(date);
    // });

    // document.getElementById("bmax").addEventListener("click", function () {
    //   let min = dateAxis.groupMin["day1"];
    //   let date = new Date(min);
    //   zoomToDates(date);
    // });

    dateAxis.events.on("selectionextremeschanged", function () {
      updateFields();
    });

    dateAxis.events.on("extremeschanged", updateFields);


    function updateFields() {
      let minZoomed = dateAxis.minZoomed + am4core.time.getDuration(dateAxis.mainBaseInterval.timeUnit, dateAxis.mainBaseInterval.count) * 0.5;
      document.getElementById("fromfield").value = x.dateFormatter.format(minZoomed, inputFieldFormat);
      document.getElementById("tofield").value = x.dateFormatter.format(new Date(dateAxis.maxZoomed), inputFieldFormat);
    };


    // fromRef.current.addEventListener("keyup", updateZoom)

    document.getElementById("fromfield").addEventListener("keyup", updateZoom);
    document.getElementById("tofield").addEventListener("keyup", updateZoom);

    let zoomTimeout;
    function updateZoom() {
      if (zoomTimeout) {
        clearTimeout(zoomTimeout);
      }
      zoomTimeout = setTimeout(function (e) {
        let start = document.getElementById("fromfield").value;
        let end = document.getElementById("tofield").value;
        if ((start.length < inputFieldFormat.length) || (end.length < inputFieldFormat.length)) {
          return;
        }
        let startDate = x.dateFormatter.parse(start, inputFieldFormat);
        let endDate = x.dateFormatter.parse(end, inputFieldFormat);

        if (startDate && endDate) {
          dateAxis.zoomToDates(startDate, endDate);
        }
      }, 500);
    };

    function zoomToDates(date) {
      let min = dateAxis.groupMin["day1"];
      let max = dateAxis.groupMax["day1"];
      dateAxis.keepSelection = true;
      //   dateAxis.start = (date.getTime() - min)/(max - min);
      //   dateAxis.end = 1;

      dateAxis.zoom({ start: (date.getTime() - min) / (max - min), end: 1 });
    };

    chart.current = x;
    // 이벤트 해제 : 해제하는 함수 등록
    return () => {
      x.dispose();
    };
    // 종목코드가 바뀌면 차트를 dispose 하도록 한다.
  }, [code]);


  // 현재 종목의 마지막 종가 
  const getPrice = async () => {
    try {
      const url = `/api/daily-price/?code=${code}`;  // 배포용
      const response = await axios.get(url);

      const url2 = `/api/company-state/?code=${code}`
      const closePrice = response.data[response.data.length - 1].close.toString()
        .replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",")
      setClosePrice(closePrice);

      setLastUpdatePrice(response.data[response.data.length - 1].date);
    } catch (error) {
      console.error(error);
    }
  };

  /* HTML */
  return (
    <div className="chart-div">
      {/* 기업명, 가격표시 */}
      <div>
        <p>
          <span style={{ fontSize: '200%' }}>{compName}</span>
          <span>
            {code} ({lastUpdatePrice})
          </span>
          
        </p>

        <p>
        <h6>[{sec_nm}]</h6>
        </p>

      </div>

      {/* <div id="controls" className="controls-div"> */}
      <div className="chart-input-div">
        기간: <input type="text" id="fromfield" className="amcharts-input" />
        ~   <input type="text" id="tofield" className="amcharts-input" />
        <span style={{ fontSize: '200%', float:"right"}}>{closePrice}원</span>
      </div>

      {/* <div className="chart-btns-div">
          <button id="b1m" className="btn btn-outline-primary">1개월</button>
          <button id="b3m" className="btn btn-outline-primary">3개월</button>
          <button id="b6m" className="btn btn-outline-primary">6개월</button>
          <button id="b1y" className="btn btn-outline-primary">1년</button>
          <button id="bytd" className="btn btn-outline-primary">연초누계</button>
          <button id="bmax" className="btn btn-outline-primary">전체</button>
        </div> */}

      {/* </div> */}

      {/* 차트 구현 코드 */}
      <div id="chartdiv" className="chart-candle-div" ></div>
    </div>
  );
};