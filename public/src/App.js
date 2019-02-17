import React, { Component } from 'react';
import './App.scss';
import SiriWave from 'siriwave';

const languages = [
  ['English', 'en'],
  ['Spanish', 'es'],
  ['French', 'fr'],
  ['Korean', 'ko']
]

class Enter extends Component {
  state = {
    text: '',
    valid: false,
    done: false
  };
  onChange = (e) => {
    const matches = e.target.value.match(/http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?/i);
    this.setState({ 
      text: matches !== null ? matches[1] : e.target.value,
      valid: matches !== null,
    });
  };
  submit = (value) => {
    this.setState({ done: true }, () => {
      setTimeout(() => {
        this.props.onEnter(this.state.text, value);
      }, 1000);
    });
  }
  componentDidMount() {
    if (window.location.hash.length > 1) {
      this.onChange({target: {value: window.location.hash.replace('#', '') }});
    }
  }
  render() {
    return (
      <div className={"enter" + (this.state.done ? ' done' : '')} id="enter-area">
        <input className={this.state.valid ? 'valid' : ''} type="text" placeholder="Enter Youtube URL" value={this.state.text} onChange={this.onChange}></input>
        <div className={this.state.valid ? 'valid' : ''}>
          {languages.map(([name, value]) => (
            <button key={value} disabled={!this.state.valid} onClick={() => this.submit(value)}>{name}</button>
          ))}
        </div>
      </div>
    );
  }
}

class Video extends Component {
  state = {
    ready: false
  };
  videoRef = React.createRef();
  componentDidMount() {
    this.videoRef.current.addEventListener('canplay', () => {
      this.setState({ ready: true });
      this.props.onReady();
    });
  }
  render() {
    return (
      <div className={"video-container" + (this.state.ready ? ' ready' : '')}>
        {this.state.ready ? null : <div className="loader">
          <div className="spinner"></div>
          <p>Converting... (this may take a while)</p>
        </div> }
        <video controls ref={this.videoRef}>
          <source src={"http://visualyze.tech/download?id=" + this.props.video + "&lang=" + this.props.lang} type="video/mp4" />
        </video>
      </div>
    )
  }
}

class App extends Component {
  state = {
    video: null,
    lang: null,
    goneWave: false
  };
  wave = null;
  updateVideo = (video, lang) => {
    this.setState({ video, lang });
  };
  componentDidMount() {
    this.wave = new SiriWave({
      container: document.getElementById('app'),
      width: window.innerWidth,
      height: window.innerHeight * 2,
      style: 'ios9',
      speed: 0.08
    });
    this.wave.start();
  }
  onReady = () => {
    this.setState({ goneWave: true });
    setTimeout(() => {
      this.wave.stop();
    }, 5000);
  }
  componentWillUnmount() {
    this.wave.stop();
  }
  render() {
    return (
      <div id="app" className={this.state.goneWave ? 'goneWave' : ''}>
        {this.state.video !== null ? <Video onReady={this.onReady} video={this.state.video} lang={this.state.lang} /> : <Enter onEnter={this.updateVideo} />}
      </div>
    );
  }
}

export default App;
