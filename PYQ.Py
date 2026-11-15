__import__("sys").dont_write_bytecode=True
import os
import random
from pathlib import Path as PathOBJ
from collections.abc import Callable
os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "WINDOWSMEDIAFOUNDATION".lower()
from PyQt5              import *
from PyQt5.QtWidgets    import *
from PyQt5.QtCore       import *
from PyQt5.QtGui        import *
from PyQt5.Qt           import *
from PyQt5.QtMultimedia import QMediaPlayer
from moviepy            import *
from moviepy.video.fx   import Margin,Freeze,Loop
from moviepy.audio.fx   import AudioLoop
from DrawShape import *
from HelpTool  import *

IMAGE_SUFFIXS = ["PNG","JPG","GIF","BMP","JPEG"]
VIDEO_SUFFIXS = ["AVI","MP4","MKV","MOV","RVMB"]

def RecFiles(DIR:str,SuffL:list[str]=IMAGE_SUFFIXS):
  L = []
  for Parent,DirNames,FileNames in os.walk(DIR):
    for FileName in FileNames:
      FilePath = os.path.join(Parent,FileName)
      Value = PathOBJ(FilePath).suffix.upper()
      if Value.replace(".","") in SuffL:
        L.append(FilePath)
  return L

DefFiles = [DeskPath+"4-1.MP4",DeskPath+"M-RIDGE.PNG"]
DefFiles = [f"{DeskPath}/A/{i}.MP4" for i in range(1,3)]
DefFiles = ["1.MP4","3.MP4","2.MP4"]
DefFiles = RecFiles(DeskPath+"MY/",[".MP4"])
DefFiles = sorted(DefFiles)
DefFiles = ["圆明园.MP4"]

def L2R(L:list[int]):
  return QRect(L[0],L[1],L[2],L[3])

def Color2RGB(Col:str):
  R = int("0X"+Col[0:2],16)
  G = int("0X"+Col[2:4],16)
  B = int("0X"+Col[4:6],16)
  return [f'RGB({R},{G},{B})',(R,G,B),[R,G,B,255]]

def SetBgMusic(Clip:VideoClip,BgMusic:str,Time:float=None):
  BgmAudio = AudioFileClip(BgMusic)
  BgmAudio = AudioLoop(duration=Time or Clip.duration).apply(BgmAudio)
  return Clip.with_audio(BgMusic)

def SetClipFreeze(Clip:VideoClip,StFzTime:float,SumTime:float,EnSameSt:bool=False,IsStBlank=False):
  Clips = []
  if StFzTime>0.01:
    Frame = "./Res/T.PNG" if IsStBlank else Clip.get_frame(0)
    ClipS = ImageClip(Frame).with_duration(StFzTime).with_fps(1)
    Clips.append(ClipS)
  Clips.append(Clip)
  if SumTime-Clip.duration-StFzTime>0.01:
    '''不减去0.5获取到的是第一帧'''
    Frame = 0 if EnSameSt else Clip.duration-0.5
    ClipE = ImageClip(Clip.get_frame(Frame)).with_duration(SumTime-Clip.duration-StFzTime).with_fps(1)
    Clips.append(ClipE)
  FinalClip = concatenate_videoclips(Clips)
  return FinalClip

def SetClipCover(Clip,ImgFile):
  OBJ = ImageClip(ImgFile).with_fps(1).with_duration(0.1).resized(Clip.size).with_position(('CENTER'.lower(),'CENTER'.lower()))
  FinalClip = CompositeVideoClip([Clip,OBJ])
  return FinalClip

def SaveClip(Clip:VideoClip,FilePath=None,IsGif=False):
  Log(Clip.size,Clip.duration)
  if not FilePath:
    FilePath = GetTimeName()
  if IsGif:
    Clip.write_gif(FilePath+".GIF")
  else:
    FFMpegParams = ["-CRF","17","-PIX_FMT","YUV420P", "-MOVFLAGS","+FASTSTART"]
    Clip.write_videofile(FilePath+".MP4",temp_audiofile = DeskPath+"../__V__.MP4",
                         audio_codec   = "aac",
                         codec         = "libx264",
                         fps           = Clip.fps,
                         bitrate       = None,
                         audio_bitrate = None,
                         ffmpeg_params = [e.lower() for e in FFMpegParams],
                         pixel_format  = None,
                         threads       = CpuCount)
  Clip.close()

def VideoFrame(Video,FilePath,Save=False):
  if isinstance(Video,str):
    ClipOBJ = VideoFileClip(Video)
  elif isinstance(Video,VideoClip):
    ClipOBJ = Video
  ImgClip = ImageClip(FilePath).with_fps(1).with_duration(ClipOBJ.duration).resized(ClipOBJ.size).with_position((0,0))
  FinalClip = CompositeVideoClip([ClipOBJ,ImgClip])
  if Save:
    SaveClip(FinalClip)
  return FinalClip

def GetCssFrame(W,H,FW,FC="008800",Style:str="GROOVE"): 
  OBJ = QLabel()
  OBJ.resize(W,H)
  OBJ.setStyleSheet(f'BACKGROUND-COLOR: TRANSPARENT;BORDER:{FW}PX {Style} #{FC}'.lower())
  QImg: QImage = OBJ.grab().toImage().convertToFormat(QImage.Format_RGBA8888)
  Data = QImg.bits().asstring(QImg.byteCount())
  return PyVips.Image.new_from_memory(Data,QImg.width(),QImg.height(),4,PyVips.BandFormat.UCHAR).copy(interpretation=PyVips.Interpretation.SRGB)

def GenMeshFrame(W,H,FW,File,FC="008800",Style="SOLID"): 
  FileName = GetCssFrame(W,H,FW,FC,Style)
  DsOBJ = DrawShape(W,H,BgColor=[255,0,0,0])
  DsOBJ.SetFrame(FW,[255,255,255,255])
  W0 = W/3
  H0 = H/3
  Sz = 11
  for i in range(1,3):
    DsOBJ.DrawRect((W0*i,0),(1,H),True)
    DsOBJ.DrawRect((0,H0*i),(W,1),True)
  if HasFile(File):
    CpOBJ = PyVips.Image.new_from_file(File)
    CpOBJ = ReSize(CpOBJ,Sz,Sz)
    for i in range(1,3):
      X = int(i*W0-Sz/2+1/2)
      Y = int(i*H0-Sz/2+1/2)
      DsOBJ.CompByOBJ(CpOBJ.copy(),(X,Y))
      DsOBJ.CompByOBJ(CpOBJ.copy(),(X,H-Y-Sz))
  DsOBJ.CompByOBJ(FileName)
  DsOBJ.SaveAs(f"M-{Style}.PNG")

class ILabel(QLabel):
  '''自定义信号,注意信号必须为类属性'''
  DelSignal = pyqtSignal(str)
  def __init__(self,Parent=None):
    super(ILabel,self).__init__(Parent)
    '''不设置的话拖动进来的图片不会显示'''
    self.setVisible(True)
    self.setContextMenuPolicy(Qt.CustomContextMenu)
    '''开放右键策略'''
    self.customContextMenuRequested.connect(self.RightMenuShow)
    '''允许拖动'''
    self.setAcceptDrops(True)
    '''内容自动适配'''
    self.setScaledContents(True)
    '''图片或视频路径'''
    self.FilePath:str = ""
    '''位置'''
    self.Pos :QPoint = QPoint(0,0)
    self.Rect:QRect  = None
    self.ParentOBJ:JigSaw = self.parent().parent()
    '''视频'''
    self.VideoVoice: bool         = True
    self.ClipOBJ   : VideoClip    = None
    self.VideoIndex: int          = 0
    self.VideoFps  : int          = 0
    self.VoiceOBJ  : QMediaPlayer = None
    self.VideoOBJ  : QVideoWidget = None
    self.VideoTimer: QTimer       = QTimer()
    self.VideoTimer.timeout.connect(self.RefVideoFrame)
    '''MASK路径'''
    self.MaskPath:str  = None
    self.MaskMark:bool = False
    '''MASK对象'''
    self.MaskOBJ:QBitmap = None
    '''动画'''
    self.GifOBJ:QMovie = None
    '''视频播放状态'''
    self.PlayPause:bool = False
    self.ImgOBJ:PyVips.Image = None
    '''图片边框'''
    self.FramePath:str = ""
    self.FrameOBJ:QLabel = QLabel(self)
    self.FrameOBJ.setScaledContents(True)
    self.FrameOBJ.setVisible(False)
    '''有遮罩后用来显示Self图片-Self设置背景色显示遮罩边框'''
    self.CopyOBJ:QLabel = QLabel(self)
    self.CopyOBJ.setScaledContents(True)
    self.CopyOBJ.setVisible(False)
    '''有遮罩后用来显示矩形颜色边框-样式会受父结点影响-不能直接放在Self上'''
    self.ColoFrame:QLabel = QLabel(self.parent())
    self.ColoFrame.setScaledContents(True)
    self.ColoFrame.setVisible(False)
    self.ColoFrame.setAttribute(Qt.WA_TransparentForMouseEvents)
    '''等比显示'''
    self.KeepScaleRate:bool = False
  
  def Delete(self):
    if self.ClipOBJ:
      self.ClipOBJ.close()
    if self.VoiceOBJ:
      self.VoiceOBJ.stop()
      self.VoiceOBJ.deleteLater()
    if self.VideoOBJ:
      self.VideoOBJ.deleteLater()
    self.ColoFrame.deleteLater()
    self.deleteLater()

  def RightMenuShow(self,Pos):
    m = QMenu(self)
    m.setStyleSheet('QMenu{MARGIN:0PX;BORDER-WIDTH:5PX;BORDER-STYLE:GROOVE;BORDER-COLOR:#55AA00;} QMenu::icon {MARGIN-LEFT:2PX} QMenu::item {FONT-SIZE:20PX;WIDTH:120PX;HEIGHT:20PX;PADDING:0PX;} QMenu::item:selected {BACKGROUND-COLOR:GRAY};')
    I = QIcon('Res/Icon.png')
    m.addAction(QAction(I, '替 换 文 件', m, triggered = self.SelFile ))
    m.addAction(QAction(I, '删 除 文 件', m, triggered = self.DelFile ))
    m.addAction(QAction(I, '设 置 样 式', m, triggered = self.SetStyle))
    m.addAction(QAction(I, '删 除 样 式', m, triggered = self.DelStyle))
    m.addAction(QAction(I, '裁 剪 尺 寸', m, triggered = self.CropSize))
    m.addAction(QAction(I, '去 掉 声 音', m, triggered = self.DelVoice))
    m.addAction(QAction(I, '保 持 比 例', m, triggered = self.SelScale))
    m.addAction(QAction(I, '打 印 信 息', m, triggered = self.LogInfo ))
    m.addAction(QAction(I, '转 成 图 片', m, triggered = self.VideoImg))
    m.triggered.connect(self.MenuSlot)
    m.exec_(QCursor.pos())

  def MenuSlot(self, ACT:QAction)->str:
    return ACT.text()

  def SelFile(self):
    if self.ClipOBJ:
      Filter = "视频("+ " ".join([f"*.{e}" for e in VIDEO_SUFFIXS])+")"
    else:
      Filter = "图片("+ " ".join([f"*.{e}" for e in IMAGE_SUFFIXS])+")"
    FilePath,ImgType = QFileDialog.getOpenFileName(self,"打开文件","",Filter)
    self.ParentOBJ.CreateLabOBJ(self,FilePath,self.GetRect())

  def DelFile(self):
    self.DelSignal.emit(self.GetFilePath())

  def SetStyle(self):
    self.MaskMark = True
    self.MaskSetChange(self.ParentOBJ.GetMaskFilePath())

  def DelStyle(self):
    self.MaskMark = False
    if self.MaskOBJ:
      self.MaskOBJ=None
      self.clear()
      self.clearMask()
      if isinstance(self.CopyOBJ.pixmap(),QPixmap):
        self.setPixmap(self.CopyOBJ.pixmap())
      self.CopyOBJ.clear()
      self.CopyOBJ.setVisible(False)
      self.setStyleSheet(self.ParentOBJ.GetNorFrameStyle())

  def CropSize(self):
    __import__("subprocess").Popen(["PYTHON CropSize.py",self.GetFilePath()])
    
  def DelVoice(self):
    self.VideoVoice = False
    self.PlayVideo(False)

  def VideoImg(self):
    if self.ClipOBJ:
      i=1
      for Frame in self.ClipOBJ.iter_frames():
        Im = PyVips.Image.new_from_array(Frame)
        Im.write_to_file(f"PIC/{i:04d}.JPG")
        i+=1

  def SelScale(self):
    self.KeepScaleRate = not self.KeepScaleRate
    self.SetRect()
  
  def LogInfo(self):
    P = self.Pos
    R = self.Rect
    Log("P:",f"({P.x()},{P.y()})","R:",f"[{R.x()},{R.y()},{R.width()},{R.height()}]","W:",self.width(),"H:",self.height())

  def DelSlot(self,Func:Callable):
    self.DelSignal.connect(Func)

  def SetPixmap(self,Pix:QPixmap):
    self.setPixmap(Pix)

  def mouseDoubleClickEvent(self,e):
    self.SelFile()

  def GetPos(self)->QPoint:
    return self.Pos

  def GetW(self)->int:
    return self.width()

  def GetH(self)->int:
    return self.height()

  def GetRect(self)->QRect:
    return self.Rect
 
  def GetFramePath(self)->str:
    return self.FramePath

  def GetFilePath(self)->str:
    return self.FilePath

  def GetImgOBJ(self)->PyVips.Image:
    return self.ImgOBJ

  def SetFrameVisible(self,Vis:bool):
    self.FrameOBJ.setVisible(Vis)
 
  def SetFrame(self,FramePath:str):
    self.FramePath = FramePath
    self.FrameOBJ.setVisible(not not FramePath)
    if FramePath:
      self.FrameOBJ.setPixmap(QPixmap(self.FramePath))

  def SetData(self,FilePath:str,PixOBJ=None,FramePath:str=""):
    self.FilePath = FilePath
    if PixOBJ:
      if isinstance(PixOBJ,QPixmap):
        self.setPixmap(PixOBJ)
      else:
        Log("Err:参数错误")
    else:
      self.setPixmap(QPixmap(FilePath))
    self.FramePath = FramePath

  def SetTop(self):
    self.raise_()
    self.ColoFrame.raise_()
    self.FrameOBJ.raise_()
    self.CopyOBJ.raise_()
  
  '''IMG跟边框是整体的-Video跟边框是分开的'''
  def SetPos(self,Pos:QPoint):
    self.Pos = Pos
    '''偏移FW让中间的边框重叠'''
    FW = self.ParentOBJ.FrameW
    if self.ParentOBJ.WeXinPyqTog.isChecked():
      FW = 0
    CW = self.ParentOBJ.CanvasW
    CH = self.ParentOBJ.CanvasH
    X0 = min(max(self.Pos.x()-FW,0),CW-self.width() )
    Y0 = min(max(self.Pos.y()-FW,0),CH-self.height())
    self.move(X0,Y0)
    self.FrameOBJ.move(0,0)
    self.CopyOBJ.move(FW,FW)
    self.ColoFrame.move(X0,Y0)

  def SetRect(self,R:QRect=None):
    R = R or self.Rect
    if not self.KeepScaleRate:
      '''修正CalcRect()相差一个像素的问题'''
      if R.x()+R.width()+1==self.ParentOBJ.CanvasW:
        R.setWidth(R.width()+1)
      if R.y()+R.height()+1==self.ParentOBJ.CanvasH:
        R.setHeight(R.height()+1)
    self.Rect = R
    self.Pos  = R.topLeft()
    FW = self.ParentOBJ.FrameW
    W0 = R.width()
    H0 = R.height()
    '''中间的边框重叠'''
    SW = FW if self.Pos.x()>0 else 0
    SH = FW if self.Pos.y()>0 else 0
    if self.ParentOBJ.WeXinPyqTog.isChecked():
      SW=SH=0
    if self.KeepScaleRate:
      if self.ClipOBJ:
        W1 = self.ClipOBJ.size[0]
        H1 = self.ClipOBJ.size[1]
      else:
        W1 = self.ImgOBJ.width
        H1 = self.ImgOBJ.height
      fS = min(W0/W1,H0/H1)
      W2 = int(W1*fS)+SW
      H2 = int(H1*fS)+SH
      '''修正误差'''
      if W2+1==R.width():
        W2+=1
      if H2+1==R.height():
        H2+=1
      self.resize(W2,H2)
    else:
      self.resize(W0+SW,H0+SH)
    '''实际尺寸'''
    RW,RH = self.width(),self.height()
    self.FrameOBJ.resize(RW,RH)
    self.CopyOBJ.resize(RW-2*FW,RH-2*FW)
    self.ColoFrame.resize(RW,RH)
    self.SetMask()
    '''尺寸设置好后再确定坐标'''
    self.SetPos(self.Pos)
    if self.ParentOBJ.IsSpecOne(self):
      self.SetTop()
 
  def SetMask(self):
    self.CopyOBJ.setVisible(False)
    self.ColoFrame.setVisible(False)
    if self.MaskOBJ:
      '''悬浮不显示颜色边框'''
      IsSpec = self.ParentOBJ.IsSpecOne(self)
      self.ColoFrame.setVisible(not IsSpec)
      if isinstance(self.pixmap(),QPixmap):
        self.CopyOBJ.setPixmap(self.pixmap())
      self.SetMaskTransform(self.CopyOBJ)
      self.CopyOBJ.setVisible(True)
      self.ColoFrame.setStyleSheet(self.ParentOBJ.GetNorFrameStyle())
      self.SetMaskTransform(self)
      '''清理后作为遮罩边框显示'''
      self.clear()
      Colors = Color2RGB(self.ParentOBJ.FrameC)
      '''设置边框样式失效'''
      self.setStyleSheet(f'BACKGROUND-COLOR:{Colors[0]};'.lower())
 
  def MaskSetChange(self,MaskPath:str=None):
    if MaskPath:
      self.MaskPath = MaskPath
      self.MaskOBJ  = QBitmap(MaskPath)
      self.SetMask()
    elif self.MaskOBJ:
      self.clearMask()
      self.MaskOBJ  = None
      self.MaskPath = None

  def SetMaskTransform(self,OBJ:QWidget):
    if self.MaskOBJ:
      OBJ.clearMask()
      T = QTransform()
      try:
        T.scale((OBJ.width())/self.MaskOBJ.width(),(OBJ.height())/self.MaskOBJ.height())
      except Exception as e:
        Log(e)
      MaskOBJ = self.MaskOBJ.transformed(T)
      OBJ.setMask(MaskOBJ) 

  def SetGIF(self,FilePath:str):
    self.FilePath=FilePath
    self.GifOBJ = QMovie(FilePath)
    self.setMovie(self.GifOBJ)
    self.GifOBJ.start()

  def SetVideo(self,FilePath:str,Loop:bool=False):
    self.FilePath = FilePath
    if self.ClipOBJ:
      self.ClipOBJ.close()
    self.ClipOBJ    = VideoFileClip(FilePath)
    self.VideoFps   = self.ClipOBJ.fps
    self.VideoIndex = 0
    self.VideoTimer.stop()
    self.VideoTimer.start(int(1000/self.VideoFps))
    if self.ClipOBJ.audio:
      if self.VoiceOBJ is None:
        self.VoiceOBJ = QMediaPlayer(self)
        '''避免输出警告信息'''
        self.VideoOBJ = QVideoWidget()
        self.VoiceOBJ.setVideoOutput(self.VideoOBJ)
        self.VoiceOBJ.error.connect(self.WhenError)
        self.VoiceOBJ.mediaStatusChanged.connect(self.WhenLoop)
      else:
        self.VoiceOBJ.stop()
      self.VoiceOBJ.setMedia(QMediaContent(QUrl.fromLocalFile(FilePath)))
      self.VoiceOBJ.play()
 
  def PlayVideo(self,Value:bool=False):
    if self.VoiceOBJ:
      if Value and self.VideoVoice:
        self.VoiceOBJ.setVolume(50)
      else:
        self.VoiceOBJ.setVolume(0)

  def RefVideoFrame(self):
    if self.ClipOBJ and not self.PlayPause:
      try:
        CurFrame = self.ClipOBJ.get_frame(self.VideoIndex/self.VideoFps-0.1)
      except Exception as e:
        Log(e)
      H,W,CH = CurFrame.shape
      o = QPixmap.fromImage(QImage(CurFrame.data,W,H,CH*W,QImage.Format_RGB888))
      if self.MaskOBJ:
        self.CopyOBJ.setPixmap(o)
      else:
        self.setPixmap(o)
      self.VideoIndex += 1
      if self.VideoIndex>=self.ClipOBJ.duration * self.VideoFps:
        self.VideoIndex = 0

  def WhenLoop(self,Status):
    if Status == QMediaPlayer.EndOfMedia:
      self.VoiceOBJ.setPosition(0)
      self.VoiceOBJ.play()

  def WhenError(self,Code:int):
    Log(f"【播放出错】{self.FilePath} 错误码:{Code}-详情:{self.VoiceOBJ.errorString()}")

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''自定义委托:下拉项强制居中'''
class CenterItemDelegate(QStyledItemDelegate):
  def initStyleOption(self,Op,Index):
    super().initStyleOption(Op,Index)
    '''设置水平+垂直居中'''
    Op.displayAlignment = Qt.AlignLeft | Qt.AlignVCenter

class IComboBox(QComboBox):
  def __init__(self,p:QWidget=None):
    super().__init__(p)
    self.setStyleSheet("QComboBox {PADDING-LEFT:3PX;BORDER:1PX SOLID #CCC} QComboBox QAbstractItemView{}")
    self.setMinimumHeight(40)
    self.setIconSize(QSize(30,30))
    self.setView(QListView())

  def showPopup(self):
    '''先执行原生弹出下拉框'''
    super().showPopup()
    Popup = self.view().window()
    PosOBJ = self.mapToGlobal(self.rect().topLeft())
    '''强制向下弹出'''
    Popup.move(PosOBJ.x(),PosOBJ.y()+self.height())

class JigSaw(QMainWindow):
  ClSignal = pyqtSignal(str)

  def GetScreenRect(self):
    Screen = QApplication.instance().primaryScreen()
    R_0 = Screen.geometry()
    R_1 = Screen.availableGeometry()
    L = R_0.left()   - R_1.left()
    T = R_0.top()    - R_1.top()
    R = R_0.right()  - R_1.right()
    B = R_0.bottom() - R_1.bottom()

  def onWinSzChange(self,SetPos=False):
    Screen = QDesktopWidget().screenGeometry()
    BW = self.BorderW
    CW = self.CanvasW
    CH = self.CanvasH
    if self.FullRlsBtn:
      MH = self.FullRlsBtn.pos().y()+self.FullRlsBtn.height()+6
      if CH<MH:
        self.SpaceTB = max(int((MH-CH-2*BW)/2),1)
      else:
        self.SpaceTB = 1
    '''H方向三条边框-V方向两条边框+加空白间距'''
    if SetPos:
      WW = CW+self.PanelRW+3*BW+2*self.SpaceLR
      WH = CH+2*BW+2*self.SpaceTB
      WX = (Screen.width() -WW)//2
      WY = (Screen.height()-WH)//2
      self.SkipRse = True
      self.setGeometry(WX+1,WY+1,WW,WH)
      self.SkipRse = False
      self.CalcRect()
    self.setWindowTitle(f"拼图小工具({CW}*{CH})")
    self.PanelL = self.PanelL or QLabel(self)
    '''加边框不会改变原大小-所以这里先把边框尺寸加上'''
    self.PanelL.setGeometry(0,0,CW+2*BW+2*self.SpaceLR,CH+2*BW+2*self.SpaceTB)
    self.PanelR = self.PanelR or QLabel(self)
    '''加边框之前'''
    self.PanelR.setGeometry(CW+BW+2*self.SpaceLR,0,self.PanelRW+2*BW,CH+2*BW+2*self.SpaceTB)
    '''图片放在个层上'''
    self.PanelC = self.PanelC or QLabel(self)
    self.PanelC.setGeometry(BW+self.SpaceLR,BW+self.SpaceTB,CW,CH)
    '''整体的边框'''
    self.PanelF = self.PanelF or QLabel(self.PanelC)
    self.PanelF.setGeometry(0,0,CW,CH)
    '''绘制层'''
    self.PanelD = self.PanelD or QLabel(self.PanelC)
    self.PanelD.setGeometry(0,0,CW,CH)

  def GenBtn(self,p,Name,Func)->QPushButton:
    Style = "QPushButton{BORDER-IMAGE: url(Res/Btn1-1.png)} QPushButton:pressed{BORDER-IMAGE: url(Res/Btn1-2.png)}"
    Btn = QPushButton(p)
    Btn.setText(Name)
    Btn.setStyleSheet(Style)
    Btn.clicked.connect(Func)
    self.ChildL.append(Btn)
    return Btn

  def __init__(self,W=804,H=575):
    super(JigSaw,self).__init__()
    self.PyqPicW    : int    = 258
    self.PyqPicH    : int    = 258
    self.PyqSpace   : int    = 15
    self.CanvasW    : int    = W
    self.CanvasH    : int    = H
    self.SkipRse    : bool   = False
    self.SpaceLR    : int    = 1
    self.SpaceTB    : int    = 1
    self.BorderW    : int    = 5
    self.PanelRW    : int    = 103
    self.CurSelI    : int    = -1
    self.PreSelI    : int    = -1
    self.PuzzleI    : int    = 0
    self.FrameW     : int    = 2
    self.ScaleW     : int    = 1
    self.FrameC     : str    = "008800"
    self.BgMusic    : str    = ""
    self.IsDrag     : bool   = False
    self.PanelL     : QLabel = None
    self.PanelR     : QLabel = None
    self.PanelC     : QLabel = None
    self.PanelF     : QLabel = None
    self.PanelD     : QLabel = None
    self.FrmSzLab   : QLabel = None      
    self.SclSzLab   : QLabel = None      
    self.SaveLayBtn : QPushButton   = None
    self.LoadLayBtn : QPushButton   = None
    self.MergRlsBtn : QPushButton   = None
    self.PartRlsBtn : QPushButton   = None
    self.FullRlsBtn : QPushButton   = None
    self.ChildL     : list[QWidget] = []
    self.LabOBJs    : list[ILabel ] = []
    self.VideoPlayer: QMediaPlayer  = QMediaPlayer(self)
    self.CsPosLabOBJ: list[QLabel]  = []
    self.onWinSzChange(True)
    for i in range(4):
      self.CsPosLabOBJ.append(QLabel(self.PanelC))
    self.setWindowIcon(QIcon('Res/Icon.png'))
    self.setAcceptDrops(True)
    self.setCursor(QCursor(QPixmap('Res/Mouse.png'),0,0))
    self.PanelL.setStyleSheet(f'BORDER:{self.BorderW}PX GROOVE #23BC23;BACKGROUND-COLOR:#FFFFFF;'.lower())
    self.PanelL.setScaledContents(True)
    self.PanelR.setPixmap(QPixmap("Res/BgR.PNG"))
    self.PanelR.setStyleSheet(f'BORDER:{self.BorderW}PX GROOVE #23BC23;'.lower())
    self.PanelR.setScaledContents(True)
    self.PanelC.setPixmap(QPixmap("Res/BgR.PNG"))
    self.PanelC.setPixmap(QPixmap("T.PNG"))
    self.PanelC.setScaledContents(True)
    self.PanelF.setScaledContents(True)
    self.PanelF.setAttribute(Qt.WA_TransparentForMouseEvents)
    self.PanelD.setScaledContents(True)
    self.PanelD.installEventFilter(self)
    self.PanelD.setPixmap(QPixmap("Res/Mask/T.PNG"))
    self.PanelD.setAttribute(Qt.WA_TransparentForMouseEvents)
    self.PanelF.stackUnder(self.PanelD)
    
    self.ClSignal.connect(self.PlayVoice)
    self.GenBtn(self,"打 开 文 件",self.SelFiles)

    '''拼图模板'''
    self.PuzzleBox = IComboBox(self)
    self.PuzzleBox.activated.connect(self.SelPuzzle)
    self.ChildL.append(self.PuzzleBox)

    self.MaskBox = IComboBox(self)
    self.MaskBox.activated.connect(self.SelMask)
    self.MaskBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    L = RecFiles("Res/MASK/M/")
    MaskM = sorted(L,key=lambda X:int(X.split("/")[-1].upper().replace(".PNG","")))
    for Path in MaskM:
      Name = Path.split("/")[-1].upper().replace(".PNG","")
      self.MaskBox.addItem(QIcon(Path),Name)
    self.MaskBox.setCurrentIndex(5)
    self.ChildL.append(self.MaskBox)

    self.SigFrameTog = self.NewCBox(H,"单 个 边 框",self.SetSigFrame)
    self.MulFrameTog = self.NewCBox(H,"多 个 边 框",self.SetMulFrame)
    self.ClipMaskTog = self.NewCBox(H,"视 频 遮 罩",self.SelClipMask)
    self.WeXinPyqTog = self.NewCBox(H,"微 信 模 式",self.SetWeXinPyq)
    self.SamePlayTog = self.NewCBox(H,"同 时 播 放")
    self.VoiceOffTog = self.NewCBox(H,"开 启 声 音",self.SetVoiceOff)
    '''先切断信号选中的时候不触发回调'''
    self.VoiceOffTog.blockSignals(True)
    self.VoiceOffTog.setCheckState(0)
    self.VoiceOffTog.blockSignals(False)

    self.KeepRateTog = self.NewCBox(H,"保 持 比 例",self.SetKeepRate)
    self.LandPortTog = self.NewCBox(H,"横 竖 切 换",self.SetLandPort)
    self.NineLineTog = self.NewCBox(H,"九 宫 格 线",self.update)
    self.CrossPosTog = self.NewCBox(H,"十 字 交 叉",self.SelCrossPos)
    self.NineLineTog.setCheckState(2)

    self.CsPosBox = IComboBox(self)
    self.CsPosBox.activated.connect(self.SelCrossPos)
    MaskM = RecFiles("Res/CpMASK/M/")
    MaskM = sorted(MaskM,key=lambda X:int(X.split("/")[-1].upper().replace(".PNG","")))
    for Path in MaskM:
      Name = Path.split("/")[-1].upper().replace(".PNG","")
      self.CsPosBox.addItem(QIcon(Path),Name)
    self.CsPosBox.setCurrentIndex(-1)
    self.ChildL.append(self.CsPosBox)
 
    self.FrmStyBox = IComboBox(self)
    self.FrmStyBox.activated.connect(self.SelFrmSty)
    self.FrmStyBox.setFixedHeight(30)
    Items = [("实线","SOLID"),("凸棱","RIDGE"),("内凹","INSET"),("圆点","DOTTED"),("短虚","DASHED"),("双线","DOUBLE"),("凹槽","GROOVE"),("外凸","OUTSET")]
    for e in Items:
      self.FrmStyBox.addItem(e[0],e[1])
    self.FrmStyBox.setItemDelegate(CenterItemDelegate(self.FrmStyBox))
    self.ChildL.append(self.FrmStyBox)

    self.FrmSzLab = QLabel("边框尺寸",self)
    self.FrmSzLab.setFixedHeight(15)
    self.FrmSzLab.setStyleSheet("FONT-SIZE:12PX;MARGIN:0PX;")
    self.ChildL.append(self.FrmSzLab)

    self.FrmSzSli = QSlider(Qt.Horizontal,self)
    self.FrmSzSli.valueChanged.connect(self.ValChange)
    self.FrmSzSli.setRange(0,20)
    self.FrmSzSli.setSingleStep(1)
    self.FrmSzSli.setPageStep(1)
    self.FrmSzSli.setValue(self.FrameW)
    self.FrmSzSli.setFixedHeight(8)
    self.FrmSzSli.setStyleSheet("""QSlider::GROOVE:HORIZONTAL{HEIGHT:8PX;BACKGROUND:#CCC} QSlider::SUB-PAGE:HORIZONTAL{BACKGROUND:#0000FF}""")
    self.ChildL.append(self.FrmSzSli)

    self.GenBtn(self,"边 框 颜 色",self.SelFrameColor)
    self.GenBtn(self,"生 成 边 框",self.GenFrameFile )

    self.SclSzLab = QLabel("缩 放 比 例",self)
    self.SclSzLab.setFixedHeight(15)
    self.SclSzLab.setStyleSheet(self.FrmSzLab.styleSheet())
    self.ChildL.append(self.SclSzLab)

    self.SclSzSli = QSlider(Qt.Horizontal,self)
    self.SclSzSli.valueChanged.connect(self.ValChange)
    self.SclSzSli.setRange(1,3)
    self.SclSzSli.setSingleStep(1)
    self.SclSzSli.setPageStep(1)
    self.SclSzSli.setValue(self.ScaleW)
    self.SclSzSli.setFixedHeight(8)
    self.SclSzSli.setStyleSheet(self.FrmSzSli.styleSheet())
    self.ChildL.append(self.SclSzSli)

    self.CvSzBox = IComboBox(self)
    self.CvSzBox.activated.connect(self.SelCanvasSize)
    self.CvSzBox.setFixedHeight(30)
    self.CvSzBox.addItems(["804*804","512*680","680*512","536*178","428*766","428*604","440*816","640*1150"])
    self.ChildL.append(self.CvSzBox)

    self.SaveLayBtn = self.GenBtn(self,"保 存 布 局",lambda:self.LocalLayData(0))
    self.LoadLayBtn = self.GenBtn(self,"加 载 布 局",lambda:self.LocalLayData(1))
    self.MergRlsBtn = self.GenBtn(self,"合 并 输 出",lambda:self.Render(True,2))
    self.PartRlsBtn = self.GenBtn(self,"发 布 预 览",lambda:self.Render(True,1))
    self.FullRlsBtn = self.GenBtn(self,"完 整 发 布",lambda:self.Render(True,0))
    QTimer.singleShot(10,self.ShowAftWinSzChange)
  
  def ShowAftWinSzChange(self):
    Files = []
    for e in DefFiles:
      if PathOBJ(e).is_file():
        Files.append(e)
    self.Files = Files
    self.SetWidgetPos()
    QTimer.singleShot(1,lambda:self.ShowFiles(self.Files,True))
    QTimer.singleShot(2,self.Ref)
  
  def NewCBox(self,H,STR,Func=None):
    CBox = QCheckBox("",self)
    if Func:
      CBox.toggled.connect(Func)
    CBStyle = "QCheckBox::INDICATOR:UNCHECKED{IMAGE:url(Res/Btn2-1.png);} QCheckBox::INDICATOR:CHECKED{IMAGE:url(Res/Btn2-2.png);}"
    CBox.setStyleSheet(CBStyle)
    pLabel = QLabel(CBox)
    pLabel.move(22,8)
    pLabel.setText(STR)
    self.ChildL.append(CBox)
    return CBox

  def SelPuzzle(self):
    Name = self.PuzzleBox.currentText()
    self.PuzzleI = int(Name.split("-")[-1])
    self.Ref()

  def GenFrameFile(self):
    FilePath = "Res/CpMask/"+self.CsPosBox.currentText()+".PNG"
    Scale = self.ScaleW
    GenMeshFrame(self.CanvasW*Scale,self.CanvasH*Scale,self.FrameW*Scale,FilePath,self.FrameC,self.FrmStyBox.currentData())

  def SelFrameColor(self):
    Col = QColorDialog.getColor()
    if Col.isValid():
      self.FrameC = Col.name().replace("#","")
      self.ValChange()
  
  def SelFrmSty(self):
    self.ValChange()

  def SelCanvasSize(self):
    Value = self.CvSzBox.currentText()
    W,H = Value.split("*")
    self.CanvasW = int(W)
    self.CanvasH = int(H)
    self.onWinSzChange(True)
  
  def GetNorFrameStyle(self):
    return f'BORDER:{self.FrameW}PX {self.FrmStyBox.currentData()} #{self.FrameC};'.lower()

  def GetSelFrameStyle(self):
    return f'BORDER:{max(self.FrameW,1)}PX {self.FrmStyBox.currentData()} RED;'.lower()

  def IsCssBorderStyle(self):
    return self.FrmStyBox.currentData()!="SOLID"

  def ValChange(self):
    if not self.FrmSzLab or not self.SclSzLab:
      return
    self.FrameW = self.FrmSzSli.value()
    self.ScaleW = self.SclSzSli.value()
    self.FrmSzLab.setText(f"边框尺寸: {self.FrameW}")
    self.SclSzLab.setText(f"缩放比例: {self.ScaleW}")
    for e in self.LabOBJs:
      Style = self.GetNorFrameStyle()
      e.setStyleSheet(Style)
      e.SetMask()
      if not self.IsDrag:
        e.SetRect()
    if self.CurSelI>=0 :
      OBJ = self.LabOBJs[self.CurSelI]
      Style = self.GetSelFrameStyle()
      if OBJ.MaskOBJ==None:
        '''选中样式'''
        OBJ.setStyleSheet(Style)
        OBJ.SetTop()
      else:
        OBJ.setStyleSheet('BACKGROUND-COLOR:RED;'.lower())
    if self.IsCssBorderStyle():
      self.PanelF.setStyleSheet(self.GetNorFrameStyle())
    else:
      self.PanelF.setStyleSheet("")
  
  def SetVoiceOff(self):
    for e in self.LabOBJs:
      if e.ClipOBJ:
        e.PlayVideo(self.VoiceOffTog.isChecked())

  def Ref(self):
    self.setFocus(True)
    nCount = len(self.LabOBJs)
    nVideo = 0
    for e in self.LabOBJs:
      if e.ClipOBJ:
        e.PlayVideo(self.VoiceOffTog.isChecked())
        nVideo+=1
    Vis = nVideo==0 and (nCount==9 or nCount==1)
    self.WeXinPyqTog.setVisible(Vis)
    self.CrossPosTog.setVisible(Vis and self.WeXinPyqTog.isChecked())
    self.PanelD.setVisible(True)
    self.PuzzleBox.clear()
    self.PuzzleBox.setCurrentIndex(-1)
    self.SigFrameTog.setVisible(nVideo==0)
    self.MulFrameTog.setVisible(nVideo==0)
    self.ClipMaskTog.setVisible(nVideo>=1)
    self.SamePlayTog.setVisible(nVideo>=2)
    self.VoiceOffTog.setVisible(nVideo>=1)
    self.SaveLayBtn.setVisible(not Vis and nCount>=1)
    self.LoadLayBtn.setVisible(not Vis)
    self.MergRlsBtn.setVisible(nVideo==nCount and nVideo>2)
    self.PartRlsBtn.setVisible(nVideo>=2)
    if nVideo==0 and self.WeXinPyqTog.isChecked() and nCount==9:
      self.SetWeXinPyq()
    elif nCount in self.NorRectInfo:
      for i in range(nCount):
        R = L2R(self.NorRectInfo[nCount][self.PuzzleI][i])
        self.LabOBJs[i].SetRect(R)
      '''self.MaskComBox.setCurrentIndex(-1)'''

      for i in range(len(self.NorRectInfo[nCount])):
        Path = f"Res/Moudle/{nCount}-{i}.PNG"
        self.PuzzleBox.addItem(QIcon(Path),f"{nCount}-{i}")
      self.PuzzleBox.blockSignals(True)
      self.PuzzleBox.setCurrentIndex(self.PuzzleI)
      self.PuzzleBox.blockSignals(False)
    elif nCount>0:
      Row = __import__("math").ceil(nCount**0.5)
      L = []
      for i in range(Row):
        for j in range(Row):
          L.append([i*self.CanvasW//Row,j*self.CanvasH//Row,self.CanvasW//Row,self.CanvasH//Row])
      self.NorRectInfo[nCount] = []
      self.NorRectInfo[nCount].append(L)
      self.Ref()
      return
    self.SelMask(1)
    self.SetWidgetPos()

  def SetWidgetPos(self):
    H = self.BorderW+1
    X = self.CanvasW+2*self.BorderW+2*self.SpaceLR+1
    for e in self.ChildL:
      e.move(X,H)
      if e.isVisible():
        H=H+e.height()+2

  def DelByName(self,FilePath):
    nCount = len(self.LabOBJs)
    IsSearch = False
    for i in range(nCount):
      e = self.LabOBJs[i]
      if e.GetFilePath()==FilePath:
        '''删除最后一个特殊的时候需要剩下的保持布局不变'''
        if i+1==nCount and self.IsSpecOne(e) and (nCount-1 in self.NorRectInfo):
          LL=self.NorRectInfo[nCount-1]
          for J in range(len(LL)):
            Flag=True
            for K in range(nCount-1):
              if LL[J][K]!=self.NorRectInfo[nCount][self.PuzzleI][K]:
                Flag=False
            if Flag:
              IsSearch=True
              self.PuzzleI=J
              break
        if self.CurSelI==i:
          self.CurSelI=i-1
        e.Delete()
        self.LabOBJs.remove(e)
        break
    for e in self.Files:
      if e==FilePath:
        self.Files.remove(e)
        break
    if not IsSearch:
      self.PuzzleI=0
    self.Ref()

  def resizeEvent(self,e:QResizeEvent):
    WinW = e.size().width()
    WinH = e.size().height()
    if self.SkipRse:
      return
    for o in self.LabOBJs:
      if o.ClipOBJ:
        '''奇数尺寸在有些播放器上无法播放'''
        if WinW%2==1: WinW = WinW-1
        if WinH%2==1: WinH = WinH-1
        break
    self.CanvasW = WinW - self.PanelRW-3*self.BorderW-2*self.SpaceLR
    self.SpaceTB = 1
    self.CanvasH = WinH - 2*self.BorderW-2*self.SpaceTB
    self.onWinSzChange(True)
    self.CurSelI = min(self.CurSelI,len(self.LabOBJs))
    if len(self.LabOBJs)==0:
      self.CurSelI = -1
    self.Ref()
    self.ValChange()
    super().resizeEvent(e)

  def PlayVoice(self,Path:str):
    if HasFile(Path):
      self.VideoPlayer.setVolume(20)
      self.VideoPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(Path)))
      self.VideoPlayer.play()

  def eventFilter(self,OBJ:QObject,e:QEvent):
    if OBJ == self.PanelD and e.type()==QEvent.Paint:
      self.Draw(None)
      return True
    else:
      return super().eventFilter(OBJ,e)

  def SetWeXinPyq(self):
    W0 = self.PyqPicW*3+self.PyqSpace*2
    H0 = self.PyqPicH*3+self.PyqSpace*2
    if self.CanvasW!=W0 or self.CanvasH!=H0:
      self.CanvasW = W0
      self.CanvasH = H0
      self.onWinSzChange(True)
    nCount = len(self.LabOBJs)
    if nCount==9:
      if self.WeXinPyqTog.isChecked():
        for i in range(nCount):
          self.LabOBJs[i].SetRect(self.PyqRectInfo[nCount][i])
      elif len(self.Files)==1 :
        self.ShowFiles(self.Files)
      else:
        self.Ref()
    else:
      self.ShowFiles(self.Files)
      '''避免卡顿'''
      '''QTimer.singleShot(1,lambda: self.ShowFiles(self.Files))'''

  def SetKeepRate(self):
    for e in self.LabOBJs:
      e.KeepScaleRate = self.KeepRateTog.isChecked()
      e.SetRect()

  def SetLandPort(self):
    self.CanvasW,self.CanvasH=self.CanvasH,self.CanvasW
    self.onWinSzChange(True)
    self.Ref()

  def SetSigFrame(self):
    if self.SigFrameTog.isChecked():
      self.MulFrameTog.setCheckState(0)
    self.SelMask(1)

  def SetMulFrame(self):
    if self.MulFrameTog.isChecked():
      self.SigFrameTog.setCheckState(0)
    self.SelMask(1)

  def SelClipMask(self):
    for e in self.LabOBJs:
      if e.ClipOBJ:
        '''排除单独设置的'''
        if not e.MaskMark and self.MaskBox.currentIndex()>=0 :
          if self.ClipMaskTog.isChecked():
            e.MaskSetChange(self.GetMaskFilePath())
          else:
            e.MaskSetChange()

  '''可以做遮罩也可以做边框'''
  def GetMaskFilePath(self):
    return "Res/Mask/"+self.MaskBox.currentText()+".PNG"

  def SelMask(self,Value):
    self.PanelF.setStyleSheet("")
    self.PanelF.clear()
    for e in self.LabOBJs:
      e.SetFrameVisible(False)
    if self.MaskBox.currentIndex()>=0:
      FilePath = self.GetMaskFilePath()
      if self.MulFrameTog.isChecked():
        for e in self.LabOBJs:
          e.SetFrame(FilePath)
          e.SetFrameVisible(True)
      elif self.SigFrameTog.isChecked():
        self.PanelF.setPixmap(QPixmap(FilePath))
    self.SelClipMask()
    self.PanelF.raise_()

  def SelCrossPos(self):
    FilePath = "Res/CpMask/"+self.CsPosBox.currentText()+".PNG"
    W0,H0 = 48,48
    W1,H1,S1 = self.PyqPicW,self.PyqPicH,self.PyqSpace
    if self.CrossPosTog.isChecked():
      Poss = [(W1+S1//2,H1+S1//2),(W1*2+S1*3//2,H1+S1//2),(W1+S1//2,H1*2+S1*3//2),(W1*2+S1*3//2,H1*2+S1*3//2)]
      for i in range(4):
        e = self.CsPosLabOBJ[i]
        e.setVisible(True)
        e.setScaledContents(True)
        e.setPixmap(QPixmap(FilePath))
        e.resize(W0,H0)
        e.move(Poss[i][0]-W0//2,Poss[i][1]-H0//2)
        e.raise_()
    else:
      for e in self.CsPosLabOBJ:
        e.setVisible(False)

  '''特殊排列的最后一个即重叠在上层的那一个-可以在任意位置'''
  def IsSpecOne(self,e):
    Count = len(self.LabOBJs)
    Index = 0
    for i in range(Count):
      if e==self.LabOBJs[i]:
        Index = i
        break
    if Index+1==Count and Count in self.SpecRctInfo:
      if self.PuzzleI>=len(self.NorRectInfo[Count])-len(self.SpecRctInfo[Count]):
        return True
    return False

  def mousePressEvent(self,e:QMouseEvent):
    '''鼠标按下事件'''
    if e.buttons()==Qt.LeftButton:
      for i in range(len(self.LabOBJs)-1,-1,-1):
        if self.LabOBJs[i].GetRect().contains(e.pos()):
          self.setFocus(True)
          self.PreSelI = self.CurSelI
          self.CurSelI = i
          mData = QMimeData()
          mData.setData("Img",QByteArray())
          Drag = QDrag(self)
          Drag.setMimeData(mData)
          self.PrePos   = e.pos()
          self.ClickPos = ""
          R = self.LabOBJs[i].GetRect()
          Space = 20
          X,Y,W,H = R.x(),R.y(),R.width(),R.height()
          if not self.WeXinPyqTog.isChecked():
            if QRect(X,Y,W,Space).contains(e.pos()):
              self.ClickPos="T"
            elif QRect(X,Y+H-Space,W,Space).contains(e.pos()):
              self.ClickPos="B"
            elif QRect(X,Y,Space,H).contains(e.pos()):
              self.ClickPos="L"
            elif QRect(X+W-Space,Y,Space,H).contains(e.pos()):
              self.ClickPos="R"
          Drag.exec(Qt.MoveAction)
          break

  def dragMoveEvent(self,e:QDragEnterEvent):
    '''拖动'''
    self.IsDrag = True
    if e.mimeData().hasFormat("Img"):
      self.LabOBJs[self.CurSelI].SetTop()
      DltPos = e.pos()-self.PrePos
      if DltPos.x()==0 and DltPos.y()==0:
        self.ValChange()
        return e.accept()

      DeltX = abs(DltPos.x())
      DeltY = abs(DltPos.y())
      if self.ClickPos in ["T","B"]:
        if DltPos.y()>0:
          '''Log("下")'''
          if self.ClickPos=="T":
            self.MoveByKey(Qt.Key_S,DeltY,True)
          elif self.ClickPos=="B":
            self.MoveByKey(Qt.Key_S,DeltY)
        elif DltPos.y()<0:
          '''Log("上")'''
          if self.ClickPos=="T":
            self.MoveByKey(Qt.Key_W,DeltY)
          elif self.ClickPos=="B":
            self.MoveByKey(Qt.Key_W,DeltY,True)
      elif self.ClickPos in ["L","R"]:
        if DltPos.x()>0:
          '''Log("右")'''
          if self.ClickPos=="L":
            self.MoveByKey(Qt.Key_D,DeltX,True)
          elif self.ClickPos=="R":
            self.MoveByKey(Qt.Key_D,DeltX)
        elif DltPos.x()<0:
          '''Log("左")'''
          if self.ClickPos=="L":
            self.MoveByKey(Qt.Key_A,DeltX)
          elif self.ClickPos=="R":
            self.MoveByKey(Qt.Key_A,DeltX,True)
      else:
        Pos = self.LabOBJs[self.CurSelI].Pos+DltPos
        self.LabOBJs[self.CurSelI].SetPos(Pos)

      self.PrePos = e.pos()
      e.setDropAction(Qt.MoveAction)
      e.accept()
      self.ValChange()
    elif e.mimeData().hasText():
      e.accept()
    else:
      e.ignore()

  def keyPressEvent(self,e:QKeyEvent):
    if 0<=self.CurSelI and self.CurSelI<len(self.LabOBJs):
      SelL = self.LabOBJs[self.CurSelI]
      SelR = SelL.GetRect()
    if e.key()==Qt.Key_Escape:
      '''关闭退出'''
      self.close()
    elif e.key()==Qt.Key_C:
      '''清除日志'''
      os.system("CLS" if IsWIN() else "CLEAR")
    elif e.key()==Qt.Key_F1:
      '''适配尺寸'''
      MaxW=MaxH=0
      for e in self.LabOBJs:
        MaxW = max(MaxW,e.x()+e.width() )
        MaxH = max(MaxH,e.y()+e.height())
      self.CanvasW = MaxW
      self.CanvasH = MaxH
      self.onWinSzChange(True)
    elif e.key()==Qt.Key_F9:
      '''输出'''
      self.Render()
    elif e.key()==Qt.Key_F10:
      '''背景音乐'''
      if self.BgMusic!="":
        self.BgMusic=""
        self.VideoPlayer.stop()
    elif e.key()==Qt.Key_F12:
      self.Render(False)
    elif e.key()==Qt.Key_R:
      '''刷新'''
      self.Ref()
    elif e.key()==Qt.Key_Equal:
      pass
    elif e.key()==Qt.Key_Minus:
      pass
    elif e.key()==Qt.Key_Space:
      '''播放与暂停'''
      for i in range(len(self.LabOBJs)):
        V = self.LabOBJs[i]
        if V.ClipOBJ and self.CurSelI==i:
          V.PlayPause = not V.PlayPause
          if V.PlayPause:
            V.VoiceOBJ.pause()
          else:
            V.VoiceOBJ.play()
    elif e.key()==Qt.Key_Delete or e.key()==Qt.Key_Alt:
      '''删除'''
      if self.CurSelI>=0 and self.CurSelI<len(self.LabOBJs):
        self.DelByName(self.LabOBJs[self.CurSelI].GetFilePath())
    elif e.key()==Qt.Key_G:
      CurIndex = self.MaskBox.currentIndex()
      if CurIndex+1<self.MaskBox.count():
        self.MaskBox.setCurrentIndex(CurIndex+1)
      self.SelMask(0)
    elif e.key()==Qt.Key_H:
      CurIndex = self.MaskBox.currentIndex()
      if CurIndex-1>=0:
        self.MaskBox.setCurrentIndex(CurIndex-1)
      self.SelMask(0)
    elif e.key()==Qt.Key_J:
      if self.PuzzleI+1<len(self.NorRectInfo[len(self.Files)]):
        self.PuzzleI = self.PuzzleI+1
        self.Ref()
    elif e.key()==Qt.Key_K:
      if self.PuzzleI-1>=0:
        self.PuzzleI = self.PuzzleI-1
        self.Ref()
    elif e.key() in [Qt.Key_Left,Qt.Key_Right,Qt.Key_Up,Qt.Key_Down]:
      if self.CurSelI>=0:
        '''X-1后宽度也会增+1故-1保持不变'''
        if e.key() in [Qt.Key_Left,Qt.Key_Right]:
          Value = -1 if e.key()==Qt.Key_Left else 1
          SelR.setX(SelR.x()+Value)
          SelR.setWidth(SelR.width()+Value)
        else:
          Value = -1 if e.key()==Qt.Key_Up else 1
          SelR.setY(SelR.y()+Value)
          SelR.setHeight(SelR.height()+Value)
        SelL.SetRect(SelR)
      elif e.key() in [Qt.Key_Left,Qt.Key_Right]:
        Value = -1 if e.key()==Qt.Key_Left else 1
        self.FrmSzSli.setValue(self.FrameW+Value)
    elif e.key() in [Qt.Key_W,Qt.Key_A,Qt.Key_S,Qt.Key_D]:
      self.MoveByKey(e.key())

  '''往上拖动如果已经到顶Y=0若ReSize=True则减小H'''
  def MoveByKey(self,Key,Step:int=1,ReSize:bool=False):
    if self.CurSelI<0 or self.WeXinPyqTog.isChecked():
      return False
    SelO = self.LabOBJs[self.CurSelI]
    SelR = SelO.GetRect()
    '''拖动悬浮对象的时候不联动其它对象'''
    if self.IsSpecOne(SelO):
      OBJs = []
    else:
      OBJs = [e for e in self.LabOBJs if e!=SelO]
    if Key==Qt.Key_W:
      if SelR.y()==0 or ReSize:
        if SelR.bottom()+1==self.CanvasH:
          return
        SelR.setHeight(SelR.height()-Step)
        SelO.SetRect(SelR)
        for V in OBJs:
          '''下'''
          R = V.GetRect()
          if SelR.bottom()+1+Step==R.y():
            R.setY(R.y()-Step)
            V.SetRect()
          elif R.y()==SelR.y() and R.height()==SelR.height()+Step:
            R.setHeight(R.height()-Step)
            V.SetRect()
      else:
        SelR.setY(SelR.y()-Step)
        SelO.SetRect(SelR)
        for V in OBJs:
          R = V.GetRect()
          if R.bottom()+1-Step==SelR.y():
            R.setHeight(R.height()-Step)
            V.SetRect()
          elif R.y()-Step==SelR.y():
            R.setY(R.y()-Step)
            V.SetRect()
    elif Key==Qt.Key_S:
      if SelR.bottom()+1>=self.CanvasH or ReSize:
        if SelR.y()==0:
          return
        SelR.setY(SelR.y()+Step)
        SelO.SetRect(SelR)
        for V in OBJs:
          '''上'''
          R = V.GetRect()
          if R.bottom()+1+Step==SelR.y():
            R.setHeight(R.height()+Step)
            V.SetRect()
          elif R.y()+Step==SelR.y():
            R.setY(R.y()+Step)
            V.SetRect()
      else:
        SelR.setHeight(SelR.height()+Step)
        SelO.SetRect(SelR)
        for V in OBJs:
          R = V.GetRect()
          if R.y()+Step==SelR.bottom()+1:
            R.setY(R.y()+Step)
            V.SetRect()
          elif R.bottom()+1+Step==SelR.bottom()+1:
            R.setHeight(R.height()+Step)
            V.SetRect()
    elif Key==Qt.Key_A:
      if SelR.x()<=0 or ReSize:
        if SelR.right()+1==self.CanvasW:
          return
        SelR.setWidth(SelR.width()-Step)
        SelO.SetRect(SelR)
        for V in OBJs:
          '''右边'''
          R = V.GetRect()
          if SelR.right()+1+Step==R.x() and SelR.y()==R.y():
            R.setX(R.x()-Step)
            V.SetRect()
          elif R.right()+1-Step==SelR.right()+1 and SelR.y()==R.y():
            R.setWidth(R.width()-Step)
            V.SetRect()
      else:
        SelR.setX(SelR.x()-Step)
        SelO.SetRect(SelR)
        for V in OBJs:
          R = V.GetRect()
          if R.right()+1-Step==SelR.x():
            R.setWidth(R.width()-Step)
            V.SetRect()
          elif R.x()-Step==SelR.x():
            R.setX(R.x()-Step)
            V.SetRect()

    elif Key==Qt.Key_D:
      if SelR.right()+1>=self.CanvasW or ReSize:
        if SelR.x()==0:
          return
        SelR.setX(SelR.x()+Step)
        SelO.SetRect(SelR)
        for V in OBJs:
          '''左'''
          R = V.GetRect()
          if R.right()+1+Step==SelR.x():
            R.setWidth(R.width()+Step)
            V.SetRect()
          elif R.x()+Step==SelR.x():
            R.setX(R.x()+Step)
            V.SetRect()
      else:
        SelR.setWidth(SelR.width()+Step)
        SelO.SetRect(SelR)
        for V in OBJs:
          R = V.GetRect()
          if R.x()+Step==SelR.right()+1:
            R.setX(R.x()+Step)
            V.SetRect()
          elif R.right()+1+Step==SelR.right()+1:
            R.setWidth(R.width()+Step)
            V.SetRect()

  def dragEnterEvent(self,e:QDragEnterEvent):
    if e.mimeData().hasFormat("Img"):
      e.accept()
    elif e.mimeData().hasImage():
      e.accept()
    elif e.mimeData().hasText():
      e.accept()
    else:
      e.ignore()

  def dragLeaveEvent(self,e:QDragEnterEvent):
    self.IsDrag = False
    if self.CurSelI>=0:
      self.LabOBJs[self.CurSelI].SetPos(self.LabOBJs[self.CurSelI].GetRect().topLeft())

  def dropEvent(self,e:QDragEnterEvent):
    '''拖动结束图片落下'''
    self.IsDrag = False
    if e.mimeData().hasFormat("Img"):
      m = self.LabOBJs[self.CurSelI]
      m.stackUnder(self.PanelF)
      '''可以拖动在任何位置'''
      if self.IsSpecOne(m):
        m.SetRect(QRect(m.GetPos().x(),m.GetPos().y(),m.GetRect().width(),m.GetRect().height()))
        '''TODO:封装'''
        m.SetTop()
        '''提升到顶层'''
        self.PanelF.raise_()
        return

      if len(self.LabOBJs)==2 and self.LabOBJs[0].GetRect()==self.LabOBJs[1].GetRect():
        '''其中一个是边框或背景故R一样(2-2)'''
        pass
      else:
        for i in range(len(self.LabOBJs)-1,-1,-1):
          if i!=self.CurSelI and self.LabOBJs[i].GetRect().contains(e.pos()):
            n = self.LabOBJs[i]
            nR,mR = n.GetRect(),m.GetRect()
            self.LabOBJs[i],self.LabOBJs[self.CurSelI]=self.LabOBJs[self.CurSelI],self.LabOBJs[i]
            self.LabOBJs[self.CurSelI].SetRect(mR)
            self.LabOBJs[i].SetRect(nR)
            self.CurSelI = i
            self.LabOBJs[i],self.LabOBJs[self.CurSelI]=self.LabOBJs[self.CurSelI],self.LabOBJs[i]
            break

      if self.CurSelI==self.PreSelI:
        self.CurSelI = -1
      m.SetRect(m.GetRect())
      e.setDropAction(Qt.MoveAction)
      e.accept()
      '''更新视频的边框'''
      self.ValChange()
      '''最后一个可能是重叠在中间的-需要在最上层不然会被挡住'''
      if self.IsSpecOne(self.LabOBJs[-1]):
        self.LabOBJs[-1].SetTop()
      self.PanelF.raise_()
    elif e.mimeData().hasText():
      e.accept()
      L = e.mimeData().text()
      L = L.replace("file://"+("/" if IsWIN() else ""),"")
      L = L.split("\n")
      IsValidFile=False
      for V1 in L:
        if V1.split(".")[-1].upper() in ["MP3"]:
          self.BgMusic = V1
          self.PlayVoice(V1)
        elif V1.split(".")[-1].upper() in IMAGE_SUFFIXS+VIDEO_SUFFIXS:
          Has=False
          for V2 in self.Files:
            if V1==V2:
              Has=True
          if not Has:
            IsValidFile=True
            ImgOBJ = self.CreateLabOBJ(None,V1,QRect(0,0,100,100))
            Add = False
            for i in range(len(self.LabOBJs)):
              if self.LabOBJs[i].GetRect().contains(e.pos()):
                self.Files.insert(i,V1)
                self.LabOBJs.insert(i,ImgOBJ)
                Add = True
                break
            if not Add:
              self.Files.append(V1)
              self.LabOBJs.append(ImgOBJ)
      if IsValidFile:
        self.PuzzleI = 0
        self.Ref()
    else:
      e.ignore()

  def CloseEvent(self,e:QCloseEvent):
    Reply = QMessageBox.question(self,'提示',"退出",QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
    if Reply==QMessageBox.Yes:
      e.accept()
    else:
      e.ignore()
  
  def closeEvent(self,e:QCloseEvent):
    self.ClearAll()

  '''绘制图形'''
  def Draw(self,QPaintEvent):
    if not self.NineLineTog.isChecked():
      return
    Pt  = QPainter(self.PanelD)
    Pen = QPen(QColor(255,0,0,255),1,Qt.SolidLine)
    Pt.setPen(Pen)
    Pt.setBrush(QColor(255,0,0))
    if self.WeXinPyqTog.isChecked():
      for i in range(1,3):
        X0 = int(i*self.PyqPicW+(i-1/2)*self.PyqSpace)
        L0 = [QLine(QPoint(X0,0),QPoint(X0,self.CanvasH)),QLine(QPoint(0,X0),QPoint(i*self.CanvasW,X0))]
        Pt.drawLines(L0)
    else:
      for i in range(3):
        X0 = int(i*self.CanvasW//3)
        Y0 = int(i*self.CanvasH//3)
        L0 = [QLine(QPoint(X0,0),QPoint(X0,self.CanvasH)),QLine(QPoint(0,Y0),QPoint(i*self.CanvasW,Y0))]
        Pt.drawLines(L0)
    Pt.setBrush(Qt.NoBrush)
    Pt.drawRect(0,0,self.CanvasW-1,self.CanvasH-1)

  def mouseDoubleClickEvent(self,e:QMouseEvent):
    self.SelFiles()

  def ClearAll(self):
    for e in self.LabOBJs:
      e.Delete()
    self.LabOBJs = []
    self.CurSelI = -1

  def SelFiles(self):
    Value = "文件("+ " ".join([f"*.{e}" for e in IMAGE_SUFFIXS+VIDEO_SUFFIXS])+")"
    FilesPath,ImgType = QFileDialog.getOpenFileNames(self,'打开多个文件',"",Value)
    if not FilesPath:
      return False
    self.Files += FilesPath
    self.PuzzleI = 0
    self.ShowFiles(self.Files)

  '''提前把布局坐标大小算出来'''
  def CalcRect(self):
    '''朋圈模式'''
    self.PyqRectInfo = {}
    '''普通模式'''
    self.NorRectInfo = {}
    Arr  = []
    
    for i in range(3):
      for j in range(3):
        I = i*3+j
        X = j*self.PyqPicW+self.PyqSpace*j
        Y = i*self.PyqPicH+self.PyqSpace*i
        Arr.append(QRect(X,Y,self.PyqPicW,self.PyqPicH))
    self.PyqRectInfo[9] = Arr
    '''根据图片数量来进行行列布局'''
    '''''''''''''''''''''1'''''''''''''''''''''
    self.NorRectInfo[1] = []
    CW = self.CanvasW
    CH = self.CanvasH
    FW = self.FrameW
    LL = []
    LL.append([0,0,CW,CH])
    self.NorRectInfo[1].append(LL)
    '''''''''''''''''''''2'''''''''''''''''''''
    self.NorRectInfo[2] = []
    '''上下'''
    LL = []
    LL.append([CW*0//2,CH*0//2,CW*1//1,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//1,CH*1//2])
    self.NorRectInfo[2].append(LL)
    '''左右'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//2,CH*1//1])
    LL.append([CW*1//2,CH*0//2,CW*1//2,CH*1//1])
    self.NorRectInfo[2].append(LL)
    '''覆盖'''
    LL=[]
    LL.append([CW*0//1,CH*0//1,CW*1//1,CH*1//1])
    LL.append([CW*0//1,CH*0//1,CW*1//1,CH*1//1])
    self.NorRectInfo[2].append(LL)

    '''''''''''''''''''''3'''''''''''''''''''''
    self.NorRectInfo[3]=[]
    '''上中下'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*1//1,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//1,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//1,CH*1//3])
    self.NorRectInfo[3].append(LL)
    '''左中右'''
    LL=[]
    LL.append([CW*0//3,CH*0//2,CW*1//3,CH*1//1])
    LL.append([CW*1//3,CH*0//2,CW*1//3,CH*1//1])
    LL.append([CW*2//3,CH*0//2,CW*1//3,CH*1//1])
    self.NorRectInfo[3].append(LL)
    '''左1右2'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//2,CH*1//1])
    LL.append([CW*1//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*1//2,CW*1//2,CH*1//2])
    self.NorRectInfo[3].append(LL)
    '''左2右1'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*0//2,CW*1//2,CH*1//1])
    self.NorRectInfo[3].append(LL)
    '''上1下2'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//1,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*1//2,CW*1//2,CH*1//2])
    self.NorRectInfo[3].append(LL)
    '''上2下1'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//1,CH*1//2])
    self.NorRectInfo[3].append(LL)

    '''''''''''''''''''''4'''''''''''''''''''''
    self.NorRectInfo[4]=[]
    '''上2下2'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*1//2,CW*1//2,CH*1//2])
    self.NorRectInfo[4].append(LL)
    '''上1下3'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//1,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//3,CH*1//2])
    LL.append([CW*1//3,CH*1//2,CW*1//3,CH*1//2])
    LL.append([CW*2//3,CH*1//2,CW*1//3,CH*1//2])
    self.NorRectInfo[4].append(LL)
    '''上3下1'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//3,CH*1//2])
    LL.append([CW*1//3,CH*0//2,CW*1//3,CH*1//2])
    LL.append([CW*2//3,CH*0//2,CW*1//3,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//1,CH*1//2])
    self.NorRectInfo[4].append(LL)
    '''左1右3'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//2,CH*1//1])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*2//3,CW*1//2,CH*1//3])
    self.NorRectInfo[4].append(LL)
    '''左3右1'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//2,CW*1//2,CH*1//1])
    self.NorRectInfo[4].append(LL)
    '''上1中2下1'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//1,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//1,CH*1//3])
    self.NorRectInfo[4].append(LL)
    '''上1下:左1右2'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//1,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*2//4,CW*1//2,CH*1//4])
    LL.append([CW*1//2,CH*3//4,CW*1//2,CH*1//4])
    self.NorRectInfo[4].append(LL)
    '''''''''''''''''''''5'''''''''''''''''''''
    self.NorRectInfo[5]=[]
    '''上3下2'''
    LL=[]
    LL.append([CW*0//3,CH*0//2,CW*1//3,CH*1//2])
    LL.append([CW*1//3,CH*0//2,CW*1//3,CH*1//2])
    LL.append([CW*2//3,CH*0//2,CW*1//3,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*1//2,CW*1//2,CH*1//2])
    self.NorRectInfo[5].append(LL)
    '''上2下3'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*0//3,CH*1//2,CW*1//3,CH*1//2])
    LL.append([CW*1//3,CH*1//2,CW*1//3,CH*1//2])
    LL.append([CW*2//3,CH*1//2,CW*1//3,CH*1//2])
    self.NorRectInfo[5].append(LL)
    '''左2右3'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*2//3,CW*1//2,CH*1//3])
    self.NorRectInfo[5].append(LL)
    '''左3右2'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*1//2,CW*1//2,CH*1//2])
    self.NorRectInfo[5].append(LL)
    '''上2中1下2'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//1,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*2//3,CW*1//2,CH*1//3])
    self.NorRectInfo[5].append(LL)
    '''上2中2下1'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//1,CH*1//3])
    self.NorRectInfo[5].append(LL)
    '''上3中1下1'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//1,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//1,CH*1//3])
    self.NorRectInfo[5].append(LL)
    '''上1中3下1'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//1,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//1,CH*1//3])
    self.NorRectInfo[5].append(LL)
    '''上1中1下3'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//1,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//1,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*2//3,CW*1//3,CH*1//3])
    self.NorRectInfo[5].append(LL)
    '''上1下4'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//1,CH*1//2])
    LL.append([CW*0//4,CH*1//2,CW*1//4,CH*1//2])
    LL.append([CW*1//4,CH*1//2,CW*1//4,CH*1//2])
    LL.append([CW*2//4,CH*1//2,CW*1//4,CH*1//2])
    LL.append([CW*3//4,CH*1//2,CW*1//4,CH*1//2])
    self.NorRectInfo[5].append(LL)
    '''上4下1'''
    LL=[]
    LL.append([CW*0//4,CH*0//2,CW*1//4,CH*1//2])
    LL.append([CW*1//4,CH*0//2,CW*1//4,CH*1//2])
    LL.append([CW*2//4,CH*0//2,CW*1//4,CH*1//2])
    LL.append([CW*3//4,CH*0//2,CW*1//4,CH*1//2])
    LL.append([CW*0//2,CH*1//2,CW*1//1,CH*1//2])
    self.NorRectInfo[5].append(LL)

    '''上1下1左1右1中1'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*2//3,CH*1//3])
    LL.append([CW*2//3,CH*0//3,CW*1//3,CH*2//3])
    LL.append([CW*1//3,CH*2//3,CW*2//3,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//3,CH*2//3])
    LL.append([CW*1//3,CH*1//3,CW*1//3,CH*1//3])
    self.NorRectInfo[5].append(LL)

    '''''''''''''''''''''6'''''''''''''''''''''
    self.NorRectInfo[6]=[]
    '''上3下3'''
    LL=[]
    LL.append([CW*0//3,CH*0//2,CW*1//3,CH*1//2])
    LL.append([CW*1//3,CH*0//2,CW*1//3,CH*1//2])
    LL.append([CW*2//3,CH*0//2,CW*1//3,CH*1//2])
    LL.append([CW*0//3,CH*1//2,CW*1//3,CH*1//2])
    LL.append([CW*1//3,CH*1//2,CW*1//3,CH*1//2])
    LL.append([CW*2//3,CH*1//2,CW*1//3,CH*1//2])
    self.NorRectInfo[6].append(LL)
    '''左3右3'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*2//3,CW*1//2,CH*1//3])
    self.NorRectInfo[6].append(LL)
    '''上1中2下3'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//1,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*2//3,CW*1//3,CH*1//3])
    self.NorRectInfo[6].append(LL)
    '''上4中1下1'''
    LL=[]
    LL.append([CW*0//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//1,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//1,CH*1//3])
    self.NorRectInfo[6].append(LL)
    '''上1中4下1'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//1,CH*1//3])
    LL.append([CW*0//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//1,CH*1//3])
    self.NorRectInfo[6].append(LL)
    '''上1中1下4'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//1,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//1,CH*1//3])
    LL.append([CW*0//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*2//3,CW*1//4,CH*1//3])
    self.NorRectInfo[6].append(LL)
    '''上2下4'''
    LL=[]
    LL.append([CW*0//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*1//2,CH*0//2,CW*1//2,CH*1//2])
    LL.append([CW*0//4,CH*1//2,CW*1//4,CH*1//2])
    LL.append([CW*1//4,CH*1//2,CW*1//4,CH*1//2])
    LL.append([CW*2//4,CH*1//2,CW*1//4,CH*1//2])
    LL.append([CW*3//4,CH*1//2,CW*1//4,CH*1//2])
    self.NorRectInfo[6].append(LL)
    '''上3下:左2右1'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*1//3,CW*2//3,CH*2//3])
    self.NorRectInfo[6].append(LL)
    '''上:左1右2下3'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*2//3,CH*2//3])
    LL.append([CW*2//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*2//3,CW*1//3,CH*1//3])
    self.NorRectInfo[6].append(LL)
    '''左:上1下2 右:上2下1'''
    LL=[]
    LL.append([CW*0//4,CH*0//3,CW*2//4,CH*2//3])
    LL.append([CW*0//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*1//3,CW*2//4,CH*2//3])
    self.NorRectInfo[6].append(LL)

    '''''''''''''''''''''7'''''''''''''''''''''
    self.NorRectInfo[7]=[]
    '''上3中2下2'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*2//3,CW*1//2,CH*1//3])
    self.NorRectInfo[7].append(LL)
    '''上2中3下2'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*2//3,CW*1//2,CH*1//3])
    self.NorRectInfo[7].append(LL)
    '''上2中2下3'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*2//3,CW*1//3,CH*1//3])
    self.NorRectInfo[7].append(LL)
    '''上1中3下3'''
    LL = []
    LL.append([CW*0//1,CH*0//3,CW*1//1,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*2//3,CW*1//3,CH*1//3])
    self.NorRectInfo[7].append(LL)
    '''上3中1下3'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//1,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*2//3,CW*1//3,CH*1//3])
    self.NorRectInfo[7].append(LL)
    '''上3中3下1'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//1,CH*1//3])
    self.NorRectInfo[7].append(LL)
    '''上1中2下4'''
    LL=[]
    LL.append([CW*0//1,CH*0//3,CW*1//1,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*2//3,CW*1//4,CH*1//3])
    self.NorRectInfo[7].append(LL)
    '''上:左1右1下4'''
    LL=[]
    LL.append([CW*0//1,CH*0//3,CW*1//2,CH*2//3])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*2//3,CW*1//4,CH*1//3])
    self.NorRectInfo[7].append(LL)
    '''''''''''''''''''''8'''''''''''''''''''''
    self.NorRectInfo[8]=[]
    '''上2中3下3'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*2//3,CW*1//3,CH*1//3])
    self.NorRectInfo[8].append(LL)
    '''上3中2下3'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*2//3,CW*1//3,CH*1//3])
    self.NorRectInfo[8].append(LL)
    '''上3中3下2'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*2//3,CW*1//2,CH*1//3])
    self.NorRectInfo[8].append(LL)

    '''上2中4下2'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*0//2,CH*2//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*2//3,CW*1//2,CH*1//3])
    self.NorRectInfo[8].append(LL)

    '''上2中2下4'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*1//3,CW*1//2,CH*1//3])
    LL.append([CW*0//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*2//3,CW*1//4,CH*1//3])
    self.NorRectInfo[8].append(LL)
    '''上:左1右3 下4'''
    LL=[]
    LL.append([CW*0//4,CH*0//4,CW*3//4,CH*3//4])
    LL.append([CW*3//4,CH*0//4,CW*1//4,CH*1//4])
    LL.append([CW*3//4,CH*1//4,CW*1//4,CH*1//4])
    LL.append([CW*3//4,CH*2//4,CW*1//4,CH*1//4])
    LL.append([CW*0//4,CH*3//4,CW*1//4,CH*1//4])
    LL.append([CW*1//4,CH*3//4,CW*1//4,CH*1//4])
    LL.append([CW*2//4,CH*3//4,CW*1//4,CH*1//4])
    LL.append([CW*3//4,CH*3//4,CW*1//4,CH*1//4])
    self.NorRectInfo[8].append(LL)
    '''''''''''''''''''''9'''''''''''''''''''''
    self.NorRectInfo[9]=[]
    '''上1中4下4'''
    LL=[]
    LL.append([CW*0//4,CH*0//3,CW*4//4,CH*1//3])
    LL.append([CW*0//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*0//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*2//3,CW*1//4,CH*1//3])
    self.NorRectInfo[9].append(LL)
    '''上4中1下4'''
    LL=[]
    LL.append([CW*0//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*0//4,CH*1//3,CW*4//4,CH*1//3])
    LL.append([CW*0//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*2//3,CW*1//4,CH*1//3])
    self.NorRectInfo[9].append(LL)
    '''上4中4下1'''
    LL=[]
    LL.append([CW*0//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*0//3,CW*1//4,CH*1//3])
    LL.append([CW*0//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*1//3,CW*1//4,CH*1//3])
    LL.append([CW*0//4,CH*2//3,CW*4//4,CH*1//3])
    self.NorRectInfo[9].append(LL)
    '''上3中3下3'''
    LL=[]
    LL.append([CW*0//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*0//3,CW*1//3,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*0//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*2//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*2//3,CW*1//3,CH*1//3])
    self.NorRectInfo[9].append(LL)
    '''上2中3下4'''
    LL=[]
    LL.append([CW*0//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*1//2,CH*0//3,CW*1//2,CH*1//3])
    LL.append([CW*0//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*1//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*2//3,CH*1//3,CW*1//3,CH*1//3])
    LL.append([CW*0//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*1//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*2//4,CH*2//3,CW*1//4,CH*1//3])
    LL.append([CW*3//4,CH*2//3,CW*1//4,CH*1//3])
    self.NorRectInfo[9].append(LL)

    self.NorRectInfo[10] = []            
    self.SpecRctInfo     = {}
    '''㊀在所有N张图片的排列情况下加上一张悬浮图片㊁变成N+1张图片的排列情况'''
    '''㊀'''
    for Key,Value in self.NorRectInfo.items():
      if Key<7:
        self.SpecRctInfo[Key+1] = []
        for i in range(len(Value)):
          for j in range(1,3):
            LL = Value[i].copy()
            LL.append([CW//(j*3),CH//(j*3),CW*j//3,CH*j//3])
            self.SpecRctInfo[Key+1].append(LL)
 
    for Row in range(1,10):
      for Col in range(1,10):
        N = Row*Col
        if N==1 or N==3 or (Row==2 and Col==2) or (Row*Col==2):
          continue
        if Row==1 or Col==1 or N>=10:
          if N not in self.NorRectInfo:
            self.NorRectInfo[N] = []
          LL = []
          W0 = CW//Col
          H0 = CH//Row
          for R in range(Row):
            for C in range(Col):
              LL.append([W0*C,H0*R,W0,H0])
          self.NorRectInfo[N].append(LL)

    '''修正因为不能整除导致相差1PX的问题'''
    for K in self.NorRectInfo:
      R = self.NorRectInfo[K]
      XM = {}
      YM = {}
      for V1 in R:
        for V2 in V1:
          XM[V2[0]] = True
          YM[V2[1]] = True
      for V1 in R:
        for V2 in V1:
          if (V2[0]+V2[2]+1) in XM:
            V2[2]+=1
          if (V2[1]+V2[3]+1) in YM:
            V2[3]+=1

    '''放在最后便于IsSpecOne用来判断特殊的'''
    '''㊁'''
    for Key,Value in self.SpecRctInfo.items():
      for i in range(len(Value)):
        if Key not in self.NorRectInfo:
          self.NorRectInfo[Key] = []
        self.NorRectInfo[Key].append(Value[i])

    Pos = [(0,0),(3,0),(4,0),(5,0),(8,0),(0,3),(8,3),(0,4),(1,4),(7,4),(8,4),(0,5),(1,5),(2,5),(4,5),(6,5),(7,5),(8,5)]
    LL  = []
    for i in range(9):
      for j in range(6):
        if (i,j) not in Pos:
          LL.append([i*CW//9,j*CH//6,CW//9,CH//6])
    self.NorRectInfo[36] = [LL]

    '''生成布局缩略图'''
    Small = False
    if Small:
      Path = "./Res/Moudle"
      DelDir(Path)
      for Key,Value in self.NorRectInfo.items():
        for i in range(len(Value)):
          DsOBJ = DrawShape(CW,CH)
          Name  = f"{Path}/{Key}-{i}.png"
          for j in range(len(Value[i])):
            R = random.randint(1,255)
            G = random.randint(1,255)
            B = random.randint(1,255)
            X = Value[i][j][0]
            Y = Value[i][j][1]
            W = Value[i][j][2]
            H = Value[i][j][3]
            OBJ = GetColorImgOBJ(W,H,[R,G,B,255])
            DsOBJ.CompFiles(QRect(X,Y,W,H),OBJ)
          DsOBJ.SetSize(50,50).SetColorFrame(1).SaveAs(Name)
  
  def LocalLayData(self,Type):
    FilePath = DeskPath+"../__L__.TXT"
    if Type==0:
      M = {
          "CW" : self.CanvasW,
          "CH" : self.CanvasH,
          "FW" : self.FrameW ,
          "SW" : self.ScaleW ,
          "PI" : self.PuzzleI,
          "FL" : []
      }
      L = []
      for e in self.LabOBJs:
        R = e.GetRect()
        L.append([R.x(),R.y(),R.width(),R.height()])
        M["FL"].append(e.GetFilePath())
      M["Lay"] = L
      M["BgM"] = self.BgMusic 
      WriteJsonData(FilePath,M)
      Log("保存成功")
    else:
      if HasFile(FilePath):
        M = ReadJsonData(FilePath)
        self.CanvasW = M["CW"]
        self.CanvasH = M["CH"]
        self.PuzzleI = M["PI"]
        self.FrmSzSli.setValue(M["FW"])
        self.SclSzSli.setValue(M["SW"])
        self.onWinSzChange(True)
        self.Ref()
        def DelayCall():
          L = M["Lay"]
          Has = len(self.LabOBJs)
          self.Files = M["FL"]
          if Has==0:
            for i in range(len(L)):
              OBJ = self.CreateLabOBJ(None,M["FL"][i],L2R(L[i]))
              self.LabOBJs.append(OBJ)
          elif len(L)==Has: 
            for i in range(len(L)):
              self.LabOBJs[i].SetRect(L2R(L[i]))
          self.BgMusic = M["BgM"]
          self.PlayVoice(M["BgM"])
          '''模板选择CB更新'''
          self.Ref()
          """右边按钮会随文件的数量显隐故需调整窗口高度"""
          self.onWinSzChange(True)
          '''TODO优化:被标准模板覆盖了故再设置一次``'''
          for i in range(len(L)):
            Log(i,L2R(L[i]))
            self.LabOBJs[i].SetRect(L2R(L[i]))
        '''避免加载卡住'''
        QTimer.singleShot(1,DelayCall)

  def ShowFiles(self,Files:list[str],Fir:bool=False):
    nCount = len(Files)
    self.WeXinPyqTog.setVisible(nCount==9 or nCount==1)
    self.CrossPosTog.setVisible(self.WeXinPyqTog.isVisible())
    self.ClearAll()
    if self.WeXinPyqTog.isChecked() and nCount==1:
      with open(Files[0],"rb") as f:
        Data = f.read()
      o = QPixmap()
      o.loadFromData(Data)
      BigImg = PyVips.Image.new_from_buffer(Data,"")
      W0 = int(o.width() /3)
      H0 = int(o.height()/3)
      for i in range(3):
        for j in range(3):
          OBJ = ILabel(self.PanelC)
          OBJ.setStyleSheet(self.GetNorFrameStyle())
          X,Y = j*W0,i*H0
          SmallImg = o.copy(X,Y,W0,H0)
          OBJ.SetData(None,SmallImg)
          OBJ.ImgOBJ = BigImg.copy().crop(X,Y,W0,H0)
          self.LabOBJs.append(OBJ)
    elif self.WeXinPyqTog.isChecked() and nCount==9:
      for i in range(nCount):
        OBJ = ILabel(self.PanelC)
        with open(Files[i],"rb") as f:
          Data = f.read()
        o = QPixmap()
        o.loadFromData(Data)
        OBJ.SetData(None,o)
        OBJ.ImgOBJ = PyVips.Image.new_from_buffer(Data,"")
        self.LabOBJs.append(OBJ)
    else:
      if nCount in self.NorRectInfo:
        R = self.NorRectInfo[nCount]
        for i in range(nCount):
          OBJ = self.CreateLabOBJ(None,Files[i],L2R(R[self.PuzzleI][i]))
          self.LabOBJs.append(OBJ)
    if not Fir:
      self.Ref()

  def CreateLabOBJ(self,OBJ,FilePath:str,R:QRect):
    OBJ = OBJ or ILabel(self.PanelC)
    OBJ.setStyleSheet(self.GetNorFrameStyle())
    '''把当前控件放到self.PanelF控件的下层'''
    OBJ.stackUnder(self.PanelF)
    OBJ.DelSlot(self.DelByName)
    Suff = FilePath.split(".")[-1].upper()
    if Suff=="GIF":
      OBJ.SetGIF(FilePath)
      OBJ.ImgOBJ = PyVips.Image.new_from_file(FilePath,access="sequential")
    elif Suff in IMAGE_SUFFIXS:
      with open(FilePath,"rb") as f:
        Data = f.read()
      o = QPixmap()
      o.loadFromData(Data)
      OBJ.SetData(FilePath,o)
      OBJ.ImgOBJ = PyVips.Image.new_from_buffer(Data,"")
    elif Suff in VIDEO_SUFFIXS:
      OBJ.SetVideo(FilePath,True)
    OBJ.SetRect(R)
    return OBJ

  '''合并多个视频-尺寸以第一个为准'''
  def ConcatVideos(self):
    CurrentTime = getPerfCounter()
    Clips = []
    for i in range(len(self.LabOBJs)):
      e = self.LabOBJs[i]
      Clip = VideoFileClip(e.ClipOBJ.filename)
      Clips.append(Clip)
      if i>0:
        Clips[i] = Clips[i].resized(Clips[0].size)
    FinalClip = concatenate_videoclips(Clips)
    if self.BgMusic:
      BgMusic = AudioFileClip(self.BgMusic)
      FinalClip = SetBgMusic(FinalClip.without_audio(),BgMusic)
    
    if self.FrameW>0:
      if self.IsCssBorderStyle():
        FinalClip = self.SetVideoFrame(FinalClip)
      else:
        Colors = Color2RGB(self.FrameC)
        MarEff = Margin(margin_size=self.FrameW,color=Colors[1])
        FinalClip = MarEff.apply(FinalClip)
    SaveClip(FinalClip)
    for e in Clips:
      e.close()
    self.MergRlsBtn.setEnabled(True)
    Log("发布COST时间: %0.1f" % (getPerfCounter()-CurrentTime))
  
  def Render(self,IsVideo:bool=True,Mode:bool=0):
    o = __import__("THREADING".lower())
    if Mode==2:
      self.MergRlsBtn.setEnabled(False)
      T = o.Thread(target=self.ConcatVideos)
    else:
      self.PartRlsBtn.setEnabled(False)
      self.FullRlsBtn.setEnabled(False)
      T = o.Thread(target=self.Handler,args=(IsVideo,Mode,))
    T.daemon = True
    T.start()

  def Handler(self,IsVideo:bool,Mode:bool=False):
    CurrentTime = getPerfCounter()
    HasVideo = not not self.BgMusic
    if not HasVideo:
      for e in self.LabOBJs:
        if e.ClipOBJ or e.GifOBJ:
          HasVideo = True
          break
    if HasVideo:
      try:
        self.MergeVideo(IsVideo,Mode)
      except Exception:
        self.ClSignal.emit(GetSoundPath(1))
        return self.MergeVideo(IsVideo,Mode)
    else:
      CssBor = self.IsCssBorderStyle()
      FrameC = Color2RGB(self.FrameC)[2]
      if CssBor:
        FrameC = [255,255,255,0]
      DsOBJ = DrawShape(self.CanvasW*self.ScaleW,self.CanvasH*self.ScaleW)
      DsOBJ.SetFrame(self.FrameW*self.ScaleW,FrameC)
      IsPyq  = self.WeXinPyqTog.isVisible() and self.WeXinPyqTog.isChecked()
      IsCsp  = self.CrossPosTog.isChecked()
      IsSigF = self.SigFrameTog.isChecked()
      IsMulF = self.MulFrameTog.isChecked()
      FileN  = len(self.Files)
      if IsPyq:
        if FileN==1:
          '''宽高比为1:1即可'''
          OBJ   = self.LabOBJs[0].GetImgOBJ()
          Size  = min(OBJ.width,OBJ.height) 
          Scale = Size/self.PyqPicW
        elif FileN==9:
          Scale = 9
          for e in self.LabOBJs:
            '''先变成正方形'''
            Size = min(e.ImgOBJ.width,e.ImgOBJ.height)
            e.ImgOBJ = ReSize(e.ImgOBJ,Size,Size)
            '''最小缩放'''
            Scale = min(Scale,Size/self.PyqPicW)
          Size = int(Scale*self.PyqPicW)
        Rect   = QRect(0,0,Size,Size)
        Space  = int(self.PyqSpace*Scale)
        FrameW = int(self.FrameW*Scale)
          
        DsOBJ = DrawShape(Size*3+2*Space)
        DsOBJ.SetFrame(FrameW,FrameC)
        Rects = []
        for i in range(3):
          for j in range(3):
            I = 3*i+j
            e = self.LabOBJs[I]
            e.ImgOBJ = ReSize(e.ImgOBJ,Size,Size)
            if e.MaskPath:
              e.ImgOBJ = SetMaskWithFrame(e.ImgOBJ,e.MaskPath(),Rect,FrameW)
            else:
              if IsMulF:
                e.ImgOBJ = CompByReSize(e.ImgOBJ,e.GetFramePath())
              if FrameW>0 and FileN==9:
                e.ImgOBJ = ColorFrame(e.ImgOBJ,1,FrameW,FrameC)
            X,Y = j*(Size+Space),i*(Size+Space)
            Rects.append(QRect(X,Y,Size,Size))
            DsOBJ.CompByOBJ(e.ImgOBJ,(X,Y))
        if IsCsp:
          FilePath = "Res/CpMask/"+self.CsPosBox.currentText()+".PNG"
          ImgOBJ = PyVips.Image.new_from_file(FilePath)
          S = Size
          W1,H1,S1 = Size,Size,Space
          Poss = [(W1+S1//2,H1+S1//2),(W1*2+S1*3//2,H1+S1//2),(W1+S1//2,H1*2+S1*3//2),(W1*2+S1*3//2,H1*2+S1*3//2)]
          for i in range(4):
            e = self.CsPosLabOBJ[i]
            I = ReSize(ImgOBJ.copy(),Scale*e.width(),Scale*e.height())
            DsOBJ.CompByOBJ(I,(Poss[i][0]-I.width//2,Poss[i][1]-I.height//2))
        if IsSigF:
          DsOBJ.CompByReSize(self.GetMaskFilePath())
        DsOBJ.Crop(Rects).SaveAs()
      else:
        Scale = self.ScaleW
        for e in self.LabOBJs:
          Rect = L2R([e.x()*Scale,e.y()*Scale,e.width()*Scale,e.height()*Scale])
          if e.GetW()>0 and e.GetH()>0:
            if e.MaskPath:
              DsOBJ.SetMaskWithFrame(e.GetFilePath(),e.MaskPath,Rect,not self.IsSpecOne(e))
            else:
              FramePath = e.GetFramePath() if self.MulFrameTog.isChecked() else None
              DsOBJ.CompFiles(Rect,e.GetImgOBJ(),FramePath,DrawFrame=True)
              if CssBor:
                FileName = self.GetCssFrame(e.width()*Scale,e.height()*Scale)
                DsOBJ.CompFiles(Rect,FileName)
          if IsSigF:
            DsOBJ.CompByReSize(e.GetFramePath())

        if CssBor:
          FileName = self.GetCssFrame(self.CanvasW*Scale,self.CanvasH*Scale)
          DsOBJ.CompFiles(QRect(0,0,self.CanvasW*Scale,self.CanvasH*Scale),FileName)
        DsOBJ.SaveAs()
    self.ClSignal.emit(GetSoundPath())
    self.PartRlsBtn.setEnabled(True)
    self.FullRlsBtn.setEnabled(True)
    Log("发布COST时间: %0.1f" % (getPerfCounter()-CurrentTime))
 
  def GetCssFrame(self,W,H):
    return GetCssFrame(W,H,self.FrameW,self.FrameC,self.FrmStyBox.currentData())

  def SetVideoFrame(self,ClipOBJ:VideoClip):
    if self.IsCssBorderStyle() and self.FrameW>0:
      o = self.GetCssFrame(ClipOBJ.size[0],ClipOBJ.size[1])
      ClipOBJ = VideoFrame(ClipOBJ,o.numpy())
    return ClipOBJ

  '''拼视频'''
  def MergeVideo(self,IsVideo:bool=True,RenderMode:bool=False):
    Colors = Color2RGB(self.FrameC)
    if self.IsCssBorderStyle():
      FrameC = [255,255,255]
    else:
      FrameC = Colors[1]
    Clips:list[VideoClip] = []
    Voics   = []
    Times   = []
    PosXY   = []
    FileN   = len(self.LabOBJs)
    FzTimes = [0]*FileN
    MaxTime = 0
    SumTime = 0
    MarEff  = Margin(margin_size=self.FrameW*self.ScaleW,color=FrameC)
    '''如果只有两个文件:一个是视频一个是图片确保图片在上面'''
    if FileN==2 and self.LabOBJs[0].ClipOBJ==None and self.LabOBJs[1].ClipOBJ:
      self.LabOBJs.reverse()

    '''封面'''
    CoOBJ = None
    Name  = "__C__.PNG"
    if HasFile(Name):
      CoOBJ = PyVips.Image.new_from_file(Name)
      CoOBJ = ReSize(CoOBJ,self.CanvasW*self.ScaleW,self.CanvasH*self.ScaleW)

    FW = self.ScaleW*self.FrameW
    for i in range(FileN):
      e  = self.LabOBJs[i]
      W0 = self.ScaleW*e.width()
      H0 = self.ScaleW*e.height()
      if e.ClipOBJ:
        '''直接使用原对象会导致闪退'''
        OBJ = VideoFileClip(e.ClipOBJ.filename)
        if RenderMode==1:
          OBJ = OBJ.subclipped(0,2)
        if not e.VideoVoice:
          OBJ = OBJ.without_audio()
        if OBJ.audio:
          Voics.append(OBJ.audio)
      else:
        Img = PyVips.Image.new_from_file(e.GetFilePath())
        '''原始图片太大会导致ImageSequenceClip失败*故先调整尺寸-时长=帧数/FPS'''
        OBJ = ImageSequenceClip([ReSize(Img,W0,H0).numpy()],fps=1)
      MaxTime = max(MaxTime,OBJ.duration or 0)
      SumTime+= OBJ.duration
      X0 = self.ScaleW*e.x()
      Y0 = self.ScaleW*e.y()
      if e.ClipOBJ and (self.ClipMaskTog.isChecked() or e.MaskOBJ):
        pass
      else:
        OBJ = OBJ.resized((W0-2*FW,H0-2*FW))
        if FW>0:
          OBJ = MarEff.apply(OBJ)
        OBJ = self.SetVideoFrame(OBJ)
        if CoOBJ and not self.IsSpecOne(e):
          OBJ = SetClipCover(OBJ,CoOBJ.crop(X0,Y0,W0,H0).numpy())
      Clips.append(OBJ)
      if i>0:
        o = Clips[i-1]
        if o:
          FzTimes[i] = FzTimes[i-1]+o.duration
        else:
          FzTimes[i] = FzTimes[i-1]
      PosXY.append((X0,Y0))

    if MaxTime==0 and self.BgMusic:
      Clip = AudioFileClip(self.BgMusic)
      MaxTime = Clip.duration
      SumTime = Clip.duration
    MaxTime -= 0.01
    SumTime -= 0.01
    '''大于5分钟:悬浮的视频(最后一个)一开始就播放否则最后轮播'''
    SameTimePlay = SumTime>300
    if SameTimePlay and self.IsSpecOne(self.LabOBJs[FileN-1]):
      PlayTime = SumTime - Clips[FileN-1].duration
    else:
      PlayTime = SumTime
    '''同时播放-轮流播放'''
    if self.SamePlayTog.isChecked():
      for i in range(FileN):
        LoopEff = Loop(duration=MaxTime)
        Clips[i] = LoopEff.apply(Clips[i])
        '''Voics[i] = AudioLoop(duration=MaxTime).apply(Voics[i])图片没声音'''
        Clips[i] = Clips[i].with_position(PosXY[i])
    else:
      for i in range(FileN):
        '''包含图片的情况'''
        e = self.LabOBJs[i]
        if e.ClipOBJ and Clips[i].duration:
          IsSpec = self.IsSpecOne(e)
          if e.ClipOBJ and (self.ClipMaskTog.isChecked() or e.MaskOBJ):
            '''2*遮罩边框+2*颜色边框(视频边框会增加整体的尺寸)'''
            W0 = self.ScaleW*e.width()
            H0 = self.ScaleW*e.height()
            '''悬浮的视频不显示矩形颜色边框'''
            Factor = 1 if IsSpec else 2
            OBJ = Clips[i].resized((W0-2*Factor*FW,H0-2*Factor*FW))
            FileName = "__M__.PNG"
            DrawShape.WhiteAlpheChange(self.GetMaskFilePath(),FW>0,FileName)
            Maskclip = ImageClip(FileName,is_mask=True).resized(OBJ.size)
            OBJ = OBJ.with_mask(Maskclip)
            os.remove(FileName)
            if FW>0:
              Factor = 0 if IsSpec else 1
              DsOBJ  = DrawShape(W0-Factor*2*FW,H0-Factor*2*FW,None,Colors[2])
              DsOBJ.CompByReSize(self.GetMaskFilePath(),o="XOR" if IsSpec else "OVER")
              FileName = "__F__.PNG"
              DsOBJ.SaveAs(FileName)
              '''作为遮罩边框'''
              FrameClip = ImageSequenceClip([FileName],fps=1).with_position((0,0)).with_duration(OBJ.duration)
              OBJ = OBJ.with_position((FW,FW))
              OBJ = CompositeVideoClip([FrameClip,OBJ])
              if not IsSpec:
                if FileN==1:
                  MarEff = Margin(margin_size=self.FrameW*self.ScaleW,color=[255,255,255])
                if self.FrameW>0:
                  OBJ = MarEff.apply(OBJ)
                OBJ = self.SetVideoFrame(OBJ)
              os.remove(FileName)
              Clips[i] = OBJ
          if IsSpec and SameTimePlay:
            Voics.pop()
            Clips[i] = Loop(duration=PlayTime).apply(Clips[i])
          else:
            Clips[i] = SetClipFreeze(Clips[i],FzTimes[i],PlayTime,True,IsSpec)
        else:
          LoopEff = Loop(duration=PlayTime)
          Clips[i]= LoopEff.apply(Clips[i])
        Clips[i] = Clips[i].with_position(PosXY[i])

    FinalClip = CompositeVideoClip(Clips,size=(self.CanvasW*self.ScaleW,self.CanvasH*self.ScaleW),bg_color=(255,255,255,0))
    FinalClip = self.SetVideoFrame(FinalClip)
    if Voics or self.BgMusic:
      LoopEff = AudioLoop(duration=FinalClip.duration)
      if self.BgMusic:
        BgMusic = AudioFileClip(self.BgMusic)
        if BgMusic.duration<FinalClip.duration:
          BgMusic = LoopEff.apply(BgMusic)
      else:
        BgMusic = None
      if self.SamePlayTog.isChecked():
        '''只考虑背景音乐'''
        OnlyBgm = False
        if BgMusic:
          if OnlyBgm:
            FinalAudio = BgMusic
          else:
            Voics.append(BgMusic)
            FinalAudio = CompositeAudioClip(Voics)
            FinalAudio = LoopEff.apply(FinalAudio)
      else:
        if BgMusic:
          if Voics:
            FinalAudio = CompositeAudioClip([concatenate_audioclips(Voics),BgMusic])
          else:
            FinalAudio = BgMusic
        else:
          FinalAudio = concatenate_audioclips(Voics)
      FinalClip = FinalClip.with_audio(FinalAudio)
    SaveClip(FinalClip,IsGif=not IsVideo)
    for e in Clips:
      e.close()

if __name__ == '__main__':
  QApplication.setAttribute(Qt.AA_EnableHighDpiScaling,True)
  QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps,True)
  App = QApplication(__import__("sys").argv)
  '''Log(QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont("A.TTF"))[0])'''
  App.setFont(QFont("FZ-2",11 if IsWIN() else 15))
  Win = JigSaw()
  Win.show()
  __import__("sys").exit(App.exec_())
