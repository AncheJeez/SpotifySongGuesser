<p align="center">
  <img height="200" src="https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/SpotifyGuesser_logo_transp.png">
  <br/>
</p>
<br/>

## Spotify Guesser
### Simple juego de musica donde puedes usar tus playlists de Spotify

## Español
> [!Warning]
> Este programa está en <b>desarrollo</b> según la API de spotify. Solo aquellos añadidos al dashboard del usuario creador del 
> programa pueden acceder a ella. Se tiene que añadir el correo a este dashboard.
> Además, se tienen que instalar ciertas dependecias, como <b>pyside6</b>, <b>pillow</b> y <b>numpy</b>.

## Información sobre las tecnologías
> [!Note]
> [Spotify API](https://developer.spotify.com/documentation/web-api)<br/><br/>
> El usuario unicamente tiene que tener su cuenta registrada en spotify y ejecutar el programa, se abrirá una pestaña en el navegador
> donde tendrá que aceptar el uso de sus datos para el programa.
>
Aceptar el uso              |  Account -> Manage apps
:-------------------------:|:-------------------------:
![](https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/accept_spotify.png)  |  ![](https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/manage_access.png)
> [!Note]
> El creador del programa para usar la API tiene registrarse en developer.spotify.com y crear un programa en el dashboard.
> <p align="center">
>  <img height="150" src="https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/dash_board_start.png">
>  <br/>
> </p>
> Donde podremos acceder a ciertas estadisticas en la propia pagina sobre nuestro programa.
> <p align="center">
>  <img height="250" src="https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/dash_board_stats.png">
>  <br/>
> </p>
> Pero mas importante, podremos acceder al Client ID y Client Secret, que son necesarios para poder usar la API de Spotify.
> <p align="center">
>  <img height="250" src="https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/dashboard_basic_info.png">
>  <br/>
>  <img height="350" src="https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/auth-client-credentials.png">
> </p>
> <br/>

>[!Note]
> Este proyecto utiliza [Spotipy](https://spotipy.readthedocs.io/en/2.24.0/) el cuál nos permite una mayor facilidad para acceder 
> a todos los end points y facilita la autoriación con el usuario.

> [!Note]
> [PySide6](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/index.html)<br/>
> [Pagina](https://doc.qt.io/qtforpython-6.6/examples/index.html) de ejemplos de PySide6 que ayudaron mucho con el proceso de interfaz

>[!Note]
> Se utiliza [pillow](https://python-pillow.org) y [numpy](https://numpy.org) para el propio juego.
> Cuando se adivinan las canciones, la propia imagen del album al que pertenece se muestra en parte censurada.
> Utilizamos pillow para poder manipular las imagenes, dibujando los rectangulos encima dependiendo de la situación en el juego.<br/>
> Y utilizamos numpy para averiguar la "media" de color de la imagen, para que corresponda el color de la censura.<br/>
> Aquí un ejemplo:
>
Fase 1                     |  Fase 2
:-------------------------:|:-------------------------:
![](https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/fase1.png)  |  ![](https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/fase2.png)
Fase 3                     |  Fase 4
![](https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/fase3.png)  |  ![](https://github.com/AncheJeez/SpotifySongGuesser/blob/main/assets/fase4.png)

## Instalación de las dependecias
> [!Tip]
> <b>Spotipy</b>: pip install spotipy --upgrade <br/>
> <b>PySide6</b>: pip install pyside6 | python -m pip install --upgrade pyside6 <br/>
> <b>Pillow</b>: pip install pillow <br/>
> <b>Numpy</b>: pip install numpy <br/>


https://forum.qt.io/topic/147961/how-to-play-sounds-using-qmediaplayer/16
