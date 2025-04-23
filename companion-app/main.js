const { app, BrowserWindow } = require('electron')
const express = require('express'), cors = require('cors'), bodyParser = require('body-parser')
const { spawn } = require('child_process')

let win
function createWindow(){ win = new BrowserWindow({width:400,height:300,webPreferences:{nodeIntegration:true}});
  win.loadFile(__dirname+'/index.html')
}
app.whenReady().then(()=>{
  createWindow()
  const server = express()
  server.use(cors())
  server.use(bodyParser.json())

  server.post('/droneCommand',(req,res)=>{
    const {action,args,script,config,uri} = req.body
    if(action==='runMain') spawn('python',['scripted_flight/main.py',...args])
    else if(action==='executeScript') spawn('python',[script])
    else if(action==='reset'){
      if(config) spawn('python',['scripted_flight/reset.py','--config',config])
      else spawn('python',['scripted_flight/reset.py','--uri',uri])
    }
    res.json({status:'ok'})
  })

  server.post('/executeCode',(req,res)=>{
    const code = req.body.code
    const fs = require('fs'), fn = __dirname+'/temp.py'
    fs.writeFileSync(fn,code)
    spawn('python',[fn]).on('close',()=> fs.unlinkSync(fn))
    res.json({status:'ok'})
  })

  server.listen(3031,()=>console.log('Companion on 3031'))
})
app.on('window-all-closed',()=>{ if(process.platform!=='darwin') app.quit() })