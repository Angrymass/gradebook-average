package com.angryass.gradebookaverage
import android.annotation.SuppressLint
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.wrapContentSize
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.text.input.TextFieldLineLimits
import androidx.compose.foundation.text.input.TextFieldState
import androidx.compose.foundation.text.input.rememberTextFieldState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ElevatedCard
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.Icon
import androidx.compose.material3.LargeFloatingActionButton
import androidx.compose.material3.ListItemDefaults
import androidx.compose.material3.MaterialShapes
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SegmentedListItem
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.toShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import com.angryass.gradebookaverage.ui.theme.AppTheme


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val listVoti = remember {
                mutableStateListOf<Voto>()

            }
            val media by remember {
                derivedStateOf {
                    val totalPeso = listVoti.sumOf { it.peso }
                    if (totalPeso > 0) {
                        listVoti.sumOf { it.voto * it.peso } / totalPeso
                    } else {
                        0.0
                    }
                }
            }

            fun newVoto(voto: Voto) {
                listVoti.add(voto)
            }

            var isDialogAggVoto by remember { mutableStateOf(false) }

            AppTheme {
                Scaffold(modifier = Modifier.fillMaxSize(), floatingActionButton = {
                    if (isDialogAggVoto) {
                        DialogAggVoto(
                            { isDialogAggVoto = false },
                            { nuovoVoto -> newVoto(nuovoVoto) })
                    }
                    LargeFloatingActionButton(
                        onClick = { isDialogAggVoto = true },
                        containerColor = MaterialTheme.colorScheme.primaryContainer,
                        contentColor = MaterialTheme.colorScheme.primary
                    ) {
                        Icon(
                            Icons.Filled.Add,
                            "Floating action button.",
                            modifier = Modifier.size(32.dp)
                        )
                    }
                }) { innerPadding ->
                    MainScreen(
                        modifier = Modifier.padding(innerPadding),
                        listVoti = listVoti,
                        media = media
                    )
                }
            }
        }
    }
}

data class Voto(
    val voto: Double, val materia: String, val peso: Int, val data: String?, val tipo: String?
)

@Composable
fun TextField(
    tp: Int, modifier: Modifier, voto: TextFieldState, materia: TextFieldState, peso: TextFieldState
) {
    val votoDouble = voto.text.toString().toDoubleOrNull()
    val pesoInt = peso.text.toString().toIntOrNull()
    val isVotoError =
        voto.text.isNotEmpty() && (!(votoDouble != null && votoDouble >= 0.0 && votoDouble <= 10.0))
    val isPesoError =
        peso.text.isNotEmpty() && (!(pesoInt != null && pesoInt >= 0 && pesoInt <= 100))
    when (tp) {
        0 -> {
            OutlinedTextField(
                modifier = modifier,
                label = {
                    Text(
                        "Inserisci voto (0.0 - 10.0)", style = MaterialTheme.typography.labelMedium
                    )
                },
                isError = isVotoError,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                state = voto,
                lineLimits = TextFieldLineLimits.MultiLine(maxHeightInLines = 1),
            )
        }

        1 -> {
            OutlinedTextField(
                modifier = Modifier.padding(4.dp),
                label = {
                    Text(
                        "Inserisci materia", style = MaterialTheme.typography.labelMedium
                    )
                },
                state = materia,
                lineLimits = TextFieldLineLimits.MultiLine(maxHeightInLines = 1),
            )
        }

        2 -> {
            OutlinedTextField(
                modifier = Modifier.padding(4.dp),
                label = {
                    Text(
                        "Inserisci peso", style = MaterialTheme.typography.labelMedium
                    )
                },
                isError = isPesoError,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                state = peso,
                lineLimits = TextFieldLineLimits.MultiLine(maxHeightInLines = 1),
            )
        }
    }
}

@Composable
fun DialogAggVoto(onDismissRequest: () -> Unit, onConfirmRequest: (Voto) -> Unit) {
    val voto = rememberTextFieldState()
    val materia = rememberTextFieldState()
    val peso = rememberTextFieldState("100")
    val votoDouble = voto.text.toString().toDoubleOrNull()
    val materiaString = materia.text.toString()
    val pesoInt = peso.text.toString().toIntOrNull()
    val isVotoError =
        voto.text.isNotEmpty() && (!(votoDouble != null && votoDouble >= 0.0 && votoDouble <= 10.0))
    val isPesoError =
        peso.text.isNotEmpty() && (!(pesoInt != null && pesoInt >= 0 && pesoInt <= 100))
    val isDialogError =
        isPesoError or isVotoError or (votoDouble == null) or (materiaString.isBlank()) or (pesoInt == null)
    Dialog(onDismissRequest = onDismissRequest) {
        Card(
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant,
            ),
        ) {
            Text(
                "Aggiungi voto",
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(
                    start = 25.dp, end = 25.dp, top = 25.dp, bottom = 10.dp
                )
            )
            Column(
                modifier = Modifier.padding(start = 16.dp, end = 16.dp, bottom = 16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Row {
                    TextField(0, Modifier.padding(4.dp), voto, materia, peso)
                }
                Row {
                    TextField(1, Modifier.padding(4.dp), voto, materia, peso)
                }
                Row {
                    TextField(2, Modifier.padding(4.dp), voto, materia, peso)
                }
                Row {
                    TextButton(onClick = onDismissRequest) {
                        Text("Annulla")
                    }
                    TextButton(enabled = !isDialogError, onClick = {
                        val nuovoVoto = Voto(
                            voto.text.toString().toDouble(),
                            materia.text.toString(),
                            peso.text.toString().toInt(),
                            null,
                            "Aggiunto"
                        )
                        onConfirmRequest(nuovoVoto)
                        onDismissRequest()
                    }) {
                        Text("Conferma")
                    }
                }
            }
        }
    }
}

@SuppressLint("DefaultLocale")
@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun MainScreen(modifier: Modifier = Modifier, listVoti: List<Voto>, media: Double) {
    LazyColumn(
        modifier
            .padding(8.dp)
            .fillMaxSize(), verticalArrangement = Arrangement.spacedBy(3.dp)
    ) {
        item {
            ElevatedCard(
                elevation = CardDefaults.cardElevation(
                    defaultElevation = 6.dp,
                ),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                ),
                modifier = Modifier
                    .padding(start = 2.dp, top = 2.dp, end = 2.dp, bottom = 8.dp)
                    .fillMaxWidth()

            ) {
                Text(
                    text = "Media Totale: ${String.format("%.2f", media)}",
                    style = MaterialTheme.typography.displayMedium,
                    modifier = Modifier
                        .fillMaxSize()
                        .wrapContentSize(Alignment.Center)
                        .padding(8.dp),
                    textAlign = TextAlign.Center,
                )
            }
        }
        itemsIndexed(listVoti.reversed()) { index, voto ->
            SegmentedListItem(
                verticalAlignment = Alignment.CenterVertically,
                leadingContent = {
                    Box(
                        contentAlignment = Alignment.Center,
                        modifier = Modifier
                            .background(
                                MaterialTheme.colorScheme.primary, MaterialShapes.Square.toShape()
                            )
                    ) {
                        Text(
                            String.format("%.2f", voto.voto),
                            style = MaterialTheme.typography.titleLarge,
                            color = MaterialTheme.colorScheme.onPrimary,
                            modifier = Modifier.padding(4.dp)
                        )
                    }
                },
                overlineContent = { voto.tipo?.let { Text(it) } },
                supportingContent = { Text("Peso: ${voto.peso}") },
                shapes = ListItemDefaults.segmentedShapes(index, listVoti.size),
                colors = ListItemDefaults.segmentedColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
                content = ({ Text(voto.materia) })
            )
        }

    }

}

@Preview(showBackground = true)
@Composable
fun MainScreenPreview() {
    val listVoti = remember {
        mutableStateListOf<Voto>()

    }
    val media by remember {
        derivedStateOf {
            val totalPeso = listVoti.sumOf { it.peso }
            if (totalPeso > 0) {
                listVoti.sumOf { it.voto * it.peso } / totalPeso
            } else {
                0.0
            }
        }
    }

    fun newVoto(voto: Voto) {
        listVoti.add(voto)
    }

    var isDialogAggVoto by remember { mutableStateOf(false) }

    AppTheme {
        Scaffold(modifier = Modifier.fillMaxSize(), floatingActionButton = {
            if (isDialogAggVoto) {
                DialogAggVoto({ isDialogAggVoto = false }, { nuovoVoto -> newVoto(nuovoVoto) })
            }
            LargeFloatingActionButton(
                onClick = { isDialogAggVoto = true },
                containerColor = MaterialTheme.colorScheme.primaryContainer,
                contentColor = MaterialTheme.colorScheme.primary
            ) {
                Icon(
                    Icons.Filled.Add, "Floating action button.", modifier = Modifier.size(32.dp)
                )
            }
        }) { innerPadding ->
            MainScreen(
                modifier = Modifier.padding(innerPadding), listVoti = listVoti, media = media
            )
        }
    }
}
