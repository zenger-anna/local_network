from gui import main_window
from com_port import com_port
from noise_immunity_coding import link


com_provider = com_port.COMProvider()
coding_provider = link.CodingProvider(com_provider)
gui = main_window.Gui(coding_provider)
