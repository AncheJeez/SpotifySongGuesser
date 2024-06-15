from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from Controlador.utils import load_translations, load_settings

class StatisticsDialog(QDialog):
    def __init__(self, correct_count, wrong_attempts, total_time, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Statistics")
        self.setFixedSize(650, 450)
        self.setStyleSheet("background-color: #191414; color: #FFFFFF")

        settings = load_settings()
        self.lenguage = settings.get('lenguage', 'en')


        layout = QVBoxLayout()

        # media de tiempo por cancion
        if correct_count > 0:
            avg_time_per_song = total_time / correct_count
        else:
            avg_time_per_song = 0.0

        # pie chart de las buenas y malas
        pie_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(pie_canvas)
        self.create_pie_chart(pie_canvas.figure, correct_count, wrong_attempts)

        # bar chart del tiempo
        bar_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(bar_canvas)
        self.create_bar_chart(bar_canvas.figure, total_time, avg_time_per_song)

        self.ok_button = QPushButton("Ok")
        self.ok_button.setStyleSheet("background-color: #1DB954; color: #191414;")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def create_pie_chart(self, figure, correct_count, wrong_attempts):
        ax = figure.add_subplot(111)
        labels = f"{load_translations(self.lenguage,'correct_txt')}", f"{load_translations(self.lenguage,'incorrect_txt')}"
        sizes = [correct_count, wrong_attempts]
        colors = ['#1DB954', '#FF0000']

        figure.patch.set_facecolor('#191414')
        ax.set_facecolor('#191414')

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)

        for text in texts:
            text.set_color('white')
        for autotext in autotexts:
            autotext.set_color('white')
            
        ax.axis('equal')
        figure.suptitle(f"{load_translations(self.lenguage,'correct_vs_incorrect')}", color='white')

    def create_bar_chart(self, figure, total_time, avg_time_per_song):
        ax = figure.add_subplot(111)
        labels = [f"{load_translations(self.lenguage,'total_time')}", f"{load_translations(self.lenguage,'avg_time')}"]
        times = [total_time, avg_time_per_song]

        figure.patch.set_facecolor('#191414')
        ax.set_facecolor('#191414')

        ax.bar(labels, times, color=['#1DB954', '#FF9900'])
        ax.set_ylabel(f"{load_translations(self.lenguage,'time_sec')}", color='white')
        ax.set_ylabel(f"{load_translations(self.lenguage,'time_sec')}", color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        
        figure.suptitle(f"{load_translations(self.lenguage,'time_stats')}",color='white')
