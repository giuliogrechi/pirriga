
<html>
<body>
<font face="ubuntu">
<?php
    date_default_timezone_set('Europe/Rome');

    $file =          '/var/www/files_test/program.txt';
    // $filelog =       '/home/pi/pirrigami/current/log.txt';
    $filelog =       '/home/giulio/Pirrigami/pirriga/log.txt';
    $data =          date('D d M y H:i:s');
    $numerovalvola = $_POST['numerovalvola'];
    $onoff =         $_POST['onoff'];
    $ora    =        $_POST['ora'];
    $minuti =        $_POST['minuti'];
    $durataore    =  $_POST['durataore'];
    $durataminuti =  $_POST['durataminuti'];
    $days = '';
    if ($_POST['lun'] == 'si'){$days .= 'lunedi,';}
    if ($_POST['mar'] == 'si'){$days .= 'martedi,';}
    if ($_POST['mer'] == 'si'){$days .= 'mercoledi,';}
    if ($_POST['gio'] == 'si'){$days .= 'giovedi,';}
    if ($_POST['ven'] == 'si'){$days .= 'venerdi,';}
    if ($_POST['sab'] == 'si'){$days .= 'sabato,';}
    if ($_POST['dom'] == 'si'){$days .= 'domenica';}

    echo 'Ora: '. $data .'<br><br>';
    echo '<table>';
    echo '<tr><td>'. 'valvola impostata:'.'</td><td>'. $numerovalvola. '<br>'. '</td></tr>';
    echo '<tr><td>'. 'impostata su: '.    '</td><td>'. $onoff. '<br>'. '</td></tr>';
    echo '<tr><td>'. 'ora impostata: '.   '</td><td>'. $ora. ':'. $minuti. '<br>'. '</td></tr>';
    echo '<tr><td>'. 'durata impostata: '.'</td><td>'. $durataore. ' ore '. $durataminuti. ' minuti <br>'. '</td></tr>';
    echo '<tr><td>'. 'giorni impostati: '. '</td><td>'.$days. '<br>'. '</td></tr>';
    echo '</table>';
    $line = $data. ','. $onoff. ','. $ora. ','. $minuti. ','. $durataore. ','. $durataminuti. ','. $days;

    $lines = array();
    $fl = fopen($file,'r');
    $lock0 = flock($fl, LOCK_SH);
    if(!$lock0){
        echo $lock0;
        echo 'errore nel lock!';
        echo '<br>programmazione non salvata';
    }
    else{
        while(! feof($fl))
          {
          $lines[] = trim(fgets($fl));
          }

        flock($fl,LOCK_UN);
    }
    fclose($fl);
    echo '<br>';
    // for ($i = 0; $i < 4; $i++){
    //     if ($numerovalvola == $i){
    //         echo '<br>----> ';
    //     }
    //     else{
    //         echo '<br>';
    //     }
    //     echo 'valvola '. $i. ': '. $lines[$i];
    //     }

    $lines[$numerovalvola] = $line;

    $program = fopen($file, 'w');
    $lock = flock($program, LOCK_EX);
    if(!$lock){
        echo $lock;
        echo 'errore nel lock!';
    }
    else{
        for ($i = 0; $i < 4; $i++){
            fwrite($program, $lines[$i]. PHP_EOL);
        }
        echo '<h3>nuova programmazione salvata</h3>';
        // echo '<br><br>Scritto ('. $line. ') nel file';
        flock($program,LOCK_UN);

    }
    fclose($program);

    // echo '<h4>nuova impostazione:</h4>';
    // for ($i = 0; $i < 4; $i++){
    //     if ($numerovalvola == $i){
    //         echo '----> ';
    //     }
    //     else{
    //         echo '';
    //     }
    //     echo 'valvola '. $i. ': '. $lines[$i]. '<br>';
    //     }

    sleep(1); #per prendere l'ultima riga aggiornata

    $lastlog = array();
    $flog = fopen($filelog,'r');
    $lock1 = flock($flog, LOCK_SH);
    if(!$lock1){
        echo $lock1;
        echo 'errore nel lock!';
    }
    else{
        while(! feof($flog))
          {
          $lastlog[] = trim(fgets($flog));
          }

        flock($flog,LOCK_UN);
    }
    fclose($flog);
    $last = count($lastlog) - 2;
    echo '<br>';

    $logsplitted = array();
    $statusswitches = array();
    $logsplitted = explode(',', $lastlog[$last]);
    for ($i = 0; $i < 4; $i++){
      $statusswitches[$i] = (int) $logsplitted[$i + 1];
    }
    for ($i = 0; $i < 4; $i++){
      $statusswitches[$i + 4] = (int) $logsplitted[$i + 9];
    }

    $linessplitted = array();
    for ($i = 0; $i < 4; $i++){
       $linessplitted[$i] = explode(',', $lines[$i]);
    }

    echo '<h2>Impostazione attuale valvole:</h2><table>';
    for ($i = 0; $i < 4; $i++ ){
      echo '<tr><td><br></td></tr>';
      echo '<tr><td><b><u>'. 'valvola '. $i. ': '. '</u></b></td>';
      if ($statusswitches[$i] == 1){
        echo '<td>interruttore su manuale</td>';
      }
      if ($statusswitches[$i] == 0){
        echo '<td>interruttore su automatico</td>';
      }
      echo '</tr>';
      echo '<tr><td><b>stato attuale:</b></td>';
      if ($statusswitches[$i + 4] == 0){
        echo '<td>spenta</td>';
      }
      if ($statusswitches[$i + 4] == 1){
        echo '<td><b>ACCESA</b></td>';
      }
      echo '</tr>';
      echo '<tr>'. '<td><b>impostata su:</b></td><td>'. $linessplitted[$i][1]. '</td></tr>';
      echo '<tr>'.'<td><b>giorni:</b></td>';
      echo '<td>';
      for ($k = 6; $k < (count($linessplitted[$i])); $k++){
          echo $linessplitted[$i][$k]. ' ';
      }
      echo '</td>';
      echo '</tr>';
      echo '<tr><td><b>alle ore: </b></td>';
      echo '<td>'. $linessplitted[$i][2]. ':'. $linessplitted[$i][3]. '</td></tr>';
      echo '<tr><td><b>per:</b></td><td>'. $linessplitted[$i][4]. ':'. $linessplitted[$i][5]. '</td></tr>';
    }
    echo '</table><br>';
    echo 'ultimo log scritto: '. $logsplitted[0];



?><br>
</font>
</body>
</html>

