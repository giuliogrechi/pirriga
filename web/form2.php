<html>
    <head>
        <title>Programmazione irrigazione</title>
    </head>
    <body>
      <font face='ubuntu'>
<?php
    // $filelog = '/home/pi/pirrigami/current/log.txt';
    $filelog = '/home/giulio/Pirrigami/pirriga/log.txt';
    $file =    '/var/www/files_test/program.txt';
    $data = date('D d M y H:i:s');

    $lines = array();
    $fl = fopen($file,'r');
    $lock0 = flock($fl, LOCK_SH);
    if(!$lock0){
        echo $lock0;
        echo 'errore nel lock!';
    }
    else{
        while(! feof($fl))
          {
          $lines[] = trim(fgets($fl));
          }

        flock($fl,LOCK_UN);
    }
    fclose($fl);

    $lastlog = array();
    $flog = fopen($filelog,'r');
    $lock1 = flock($flog, LOCK_SH);
    if(!$lock1){
        echo $lock1;
        echo 'errore nel lock!<br>';
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
    echo '</table>';
?>


		<h2>Regolazione valvole</h2>
		<form action='process.php' method='post'>
			<br>Valvola da impostare:
	       <select name='numerovalvola'>
	       <option value='0'>0</option>
	       <option value='1'>1</option>
	       <option value='2'>2</option>
	       <option value='3'>3</option>
	       <br>
			<input type='radio' name='onoff' value='on'>on
			<input type='radio' name='onoff' value='off' checked='yes'>off<p>

		<table>
			<tr>
				<td>Inizio:
				</td>
				<td>
				ora
				<select name='ora'>
	       <option value='00'>00</option>
	       <option value='01'>01</option>
	       <option value='02'>02</option>
	       <option value='03'>03</option>
	       <option value='04'>04</option>
	       <option value='05'>05</option>
	       <option value='06'>06</option>
	       <option value='07'>07</option>
	       <option value='08'>08</option>
	       <option value='09'>09</option>
	       <option value='10'>10</option>
          <option value='11'>11</option>
          <option value='12'>12</option>
          <option value='13'>13</option>
          <option value='14'>14</option>
          <option value='15'>15</option>
          <option value='16'>16</option>
          <option value='17'>17</option>
          <option value='18'>18</option>
          <option value='19'>19</option>
          <option value='20'>20</option>
          <option value='21'>21</option>
          <option value='22'>22</option>
          <option value='23'>23</option>
          </select>
				Minuti:
	       <select name='minuti'>
	       <option value='00'>00</option>
	       <option value='15'>15</option>
	       <option value='30'>30</option>
	       <option value='45'>45</option>
          </select>
          </td>
			</tr>
			<tr>
				<td>Durata: </td>
				<td>ore
          <select name='durataore'>
            <option value='00'>00</option>
	       <option value='01'>01</option>
	       <option value='02'>02</option>
	       <option value='03'>03</option>
	       <option value='04'>04</option>
	       <option value='05'>05</option>
	       <option value='06'>06</option>
	       <option value='07'>07</option>
	       <option value='08'>08</option>

          </select>
			 Minuti:
	       <select name='durataminuti'>
	       <option value='00'>00</option>
	       <option value='15'>15</option>
	       <option value='30'>30</option>
	       <option value='45'>45</option>
          </select>
          </td>
		</tr>
	</table>
			<p>
          <input type='checkbox' name='lun' value='si'>lun
          <input type='checkbox' name='mar' value='si'>mar
          <input type='checkbox' name='mer' value='si'>mer
          <input type='checkbox' name='gio' value='si'>gio
          <input type='checkbox' name='ven' value='si'>ven
          <input type='checkbox' name='sab' value='si'>sab
          <input type='checkbox' name='dom' value='si'>dom<p>
		<input type='submit'/>
		</form>
        <br>
        <?php
            // echo $lastlog[$last];
            // echo '<br>'.$data;
            echo '<br><br>ultimo log scritto: '. $logsplitted[0];
        ?>
        </font>
	</body>
</html>
