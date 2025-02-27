//import logo from './logo.svg';
import './App.css';
import { useState } from 'react';

function App() {
  const [num, setCount] = useState(0);

  function handleClick() {
    setCount(num + 1);
  }

    
  return (
    // <div className="App">
    //   <header className="App-header">
    //     <img src={logo} className="App-logo" alt="logo" />
    //     <p>
    //       Edit <code>src/App.js</code> and save to reload.
    //     </p>
    //     <a
    //       className="App-link"
    //       href="https://reactjs.org"
    //       target="_blank"
    //       rel="noopener noreferrer"
    //     >
    //       Learn React
    //     </a>
    //   </header>
    // </div>
    <div className="App1">
      <header className="App-header">
        {/* <form> */}
          <div>
            <span contenteditable="true" placeholder="Enter text"/>
            <Button onClick={clickMe} type="button"> Search </Button>
          </div>
          <button onClick={handleClick}>
            You pressed me {num} times
          </button>
        {/* </form> */}
      </header>
    </div>
  );
}

function clickMe() {
  alert("You clicked me!");
}

function Button({ onClick, children }) {
  return (
    <button onClick={onClick}>
      {children}
    </button>
  );
}

export default App;
