// 최상위 루트 파일

import React from 'react';
import ReactDOM from 'react-dom';

// Apps
import Routing from './apps/Router';

// css
import "bootstrap/dist/css/bootstrap.min.css"

// react-redux
import CreateStore from './store/index';
import { Provider } from 'react-redux';
import rootReducer from './modules/RootReducer';

//react-router-dom
import { BrowserRouter } from 'react-router-dom';


// createStore 메소드를 이용하여, 이를 인자로 reducer을 전달해 줘야 한다.

const devTools = 
  window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__();

const store = CreateStore(rootReducer, devTools);  // reducer를 바탕으로 store 생성

  ReactDOM.render(
    <React.StrictMode>
      <BrowserRouter>
        <Provider store={store}>
             <Routing />
        </Provider>  
      </BrowserRouter>
    </React.StrictMode>,
    document.getElementById('root')
  );

// store.subscribe(LISTENER) 형태다. dispatch 메소드가 실행되면 (Button 컴포넌트 또는 다른 컴포넌트에서 dispatch 메소드가 실행되면)
// LISTENER함수가 실행된다. 그렇기 때문에 데이터가 변경 될 때만 다시 랜더링 된다.
// 이는 react-redux를 사용할때 Provider로 대체가 가능한듯 하다?
  // store.subscribe(render);
  // render();


