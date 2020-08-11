from qgreenland.tasks.common.fetch import FetchDataFiles
from qgreenland.tasks.common.misc import UngzipMany
from qgreenland.tasks.common.shapefile import Ogr2OgrShapefile
from qgreenland.util.luigi import LayerPipeline


class GzippedShapefileParts(LayerPipeline):

    def requires(self):
        fetch_data = FetchDataFiles(
            source_cfg=self.cfg['source'],
            output_name=self.cfg['id']
        )  # ->
        unzip = UngzipMany(
            requires_task=fetch_data,
            layer_id=self.layer_id
        )  # ->
        return Ogr2OgrShapefile(
            requires_task=unzip,
            layer_id=self.layer_id
        )
