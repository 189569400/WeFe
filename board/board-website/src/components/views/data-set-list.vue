<template>
    <div class="data-set-list">
        <div class="flexbox">
            <el-alert
                v-if="containsY === 'true'"
                :title="containsY === 'true' ? '注意: 发起方只能选择[包含] y 值的数据集' : ''"
                :closable="false"
                type="warning"
            />
            <slot name="data-add">
                <div
                    v-if="dataAddBtn"
                    class="data-add mb10"
                    :style="containsY != 'true' || containsY !== 'false' ? 'width: 100%;':''"
                >
                    <router-link
                        :to="{ name: 'data-add' }"
                        target="_blank"
                    >
                        <el-button style="display:block;" type="primary" size="mini">
                            上传数据集
                            <el-icon>
                                <elicon-arrow-right />
                            </el-icon>
                        </el-button>
                    </router-link>
                </div>
            </slot>
        </div>

        <el-table
            v-loading="tableLoading"
            max-height="500"
            :data="list"
            stripe
            border
        >
            <template #empty>
                <EmptyData />
            </template>
            <el-table-column
                label="名称 / Id"
                min-width="220"
            >
                <template v-slot="scope">
                    <div :title="scope.row.description">
                        {{ scope.row.name }}
                        <p class="p-id">{{ scope.row.data_set_id || scope.row.id }}</p>
                    </div>
                </template>
            </el-table-column>
            <el-table-column
                v-if="auditStatus"
                label="授权情况"
                min-width="80"
            >
                <template v-slot="scope">
                    <el-tag v-if="scope.row.audit_status === 'agree'">已授权</el-tag>
                    <el-tag
                        v-else
                        type="danger"
                    >
                        {{ scope.row.audit_status === 'disagree' ? '已拒绝' : '等待授权' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column
                label="包含Y"
                min-width="60"
            >
                <template v-slot="scope">
                    <el-tag :type="scope.row.contains_y ? 'success' : 'warning'">{{ scope.row.contains_y ? "是" : "否" }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column
                label="关键词"
                min-width="120"
            >
                <template v-slot="scope">
                    <template v-if="scope.row.tags">
                        <template v-for="(item, index) in scope.row.tags.split(',')" :key="index">
                            <el-tag
                                v-show="item"
                                class="mr10"
                            >
                                {{ item }}
                            </el-tag>
                        </template>
                    </template>
                </template>
            </el-table-column>
            <el-table-column
                label="数据信息"
                prop="row_count"
                min-width="140"
            >
                <template v-slot="scope">
                    特征量：{{ scope.row.feature_count }}
                    <br>
                    样本量：{{ scope.row.row_count }}
                    <template v-if="scope.row.contains_y && scope.row.y_positive_example_count">
                        <br>
                        正例样本数量：{{ scope.row.y_positive_example_count }}
                        <br>
                        正例样本比例：{{(scope.row.y_positive_example_ratio * 100).toFixed(1)}}%
                    </template>
                </template>
            </el-table-column>
            <el-table-column
                label="参与任务次数"
                prop="usage_count_in_job"
                min-width="110"
            />
            <el-table-column
                label="上传时间"
                min-width="160"
            >
                <template v-slot="scope">
                    {{ scope.row.creator_nickname }}<br>
                    {{ dateFormat(scope.row.created_time) }}
                </template>
            </el-table-column>
            <el-table-column
                fixed="right"
                label="选择数据集"
                width="140px"
            >
                <template v-slot="scope">
                    <slot name="operation">
                        <div class="cell-reverse">
                            <el-tooltip
                                v-if="is_my_data_set"
                                content="预览数据"
                                placement="top"
                            >
                                <el-button
                                    circle
                                    type="info"
                                    @click="showDataSetPreview(scope.row)"
                                >
                                    <el-icon>
                                        <elicon-view />
                                    </el-icon>
                                </el-button>
                            </el-tooltip>
                            <el-switch
                                v-model="scope.row.$checked"
                                :disabled="scope.row.deleted || scope.row.$unchanged || scope.row.audit_status === 'disagree' || scope.row.audit_status === 'auditing'"
                                active-color="#35c895"
                                @change="isFlow ? selectDataSet(scope.row, scope.$index) : selectMemberSwitch(scope.row, scope.$index)"
                            />
                        </div>
                    </slot>
                </template>
            </el-table-column>
        </el-table>
        <div
            v-if="pagination.total"
            :class="['pagination', 'text-r', 'confirm-bar']"
        >
            <el-pagination
                :pager-count="5"
                :total="pagination.total"
                :page-sizes="[10, 20, 30, 40, 50]"
                :page-size="pagination.page_size"
                :current-page="pagination.page_index"
                layout="total, sizes, prev, pager, next, jumper"
                @current-change="currentPageChange"
                @size-change="pageSizeChange"
            />
            <div v-if="!isFlow" class="confirm-bar">
                <p>已选择 <span>{{ checkedCount }}</span> 项</p>
                <el-button
                    type="primary"
                    :disabled="!checkedCount"
                    @click="addConfirm"
                >
                    确定添加
                </el-button>
            </div>
        </div>

        <el-dialog
            title="数据预览"
            v-model="dataSetPreviewDialog"
            destroy-on-close
            append-to-body
        >
            <DataSetPreview ref="DataSetPreview" />
        </el-dialog>
    </div>
</template>

<script>
    import table from '@src/mixins/table';
    import DataSetPreview from '@comp/views/data_set-preview';

    export default {
        components: {
            DataSetPreview,
        },
        mixins: [table],
        props:  {
            api:         Object,
            containsY:   String,
            auditStatus: Boolean,
            dataAddBtn:  {
                type:    Boolean,
                default: true,
            },
            searchField: {
                type:    Object,
                default: _ => {},
            },
            paramsExclude: Array,
            emitEventName: String,
            dataSets:      Array,
            isShow:        Boolean,
        },
        emits: ['list-loaded', 'close-dialog', 'selectDataSet', 'batchDataSet'],
        data() {
            return {
                is_my_data_set:       false,
                dataSetPreviewDialog: false,

                tableLoading:    false,
                watchRoute:      false,
                turnPageRoute:   false,
                checkAll:        false,
                isIndeterminate: false,
                checkedList:     [],
                isFlow:          false, // flow detail page
                oldCheckedList:  [],    // checked list from parent component
                batchList:       [],
                isShowData:      false,
            };
        },
        computed: {
            checkedCount() {
                let total = 0;

                this.list.forEach(item => {
                    if (item.$checked) {
                        total++;
                    }
                });
                return total;
            },
        },
        watch: {
            isShow: {
                handler(val) {
                    if (val) {
                        this.batchList = [];
                    }
                },
            },
        },
        methods: {
            // preview dataset
            showDataSetPreview(item){
                this.dataSetPreviewDialog = true;

                this.$nextTick(() =>{
                    this.$refs['DataSetPreview'].loadData(item.id);
                });
            },

            async getDataList({
                url,
                to,
                resetPagination,
                is_my_data_set = false,
                $data_set,
            }) {
                this.is_my_data_set = is_my_data_set;

                this.getListApi = url;
                this.checkAll = false;
                this.tableLoading = true;
                this.isIndeterminate = false;
                this.search = this.searchField;
                if(this.search) {
                    if(this.containsY === 'true') {
                        this.search.contains_y = true;
                    } else if (this.containsY === 'false') {
                        this.search.contains_y = false;
                    }
                }
                this.unUseParams = this.$props.paramsExclude;
                await this.getList({ to, resetPagination });

                this.oldCheckedList = $data_set || [];
                this.list.forEach((item, index) => {
                    item.$checked = false;
                    item.$unchanged = false;
                    this.list[index] = item;
                    this.oldCheckedList.find(sitem => {
                        if (item.id === sitem.data_set_id ) {
                            item.$checked = true;
                            item.$unchanged = true;
                        }
                    });
                });
                setTimeout(() => {
                    this.tableLoading = false;
                }, 300);
            },

            afterTableRender() {
                this.$emit('list-loaded', this.list);
            },

            selectAllChange(val) {
                this.checkAll = val;
                this.isIndeterminate = false;
                this.list.forEach((item, index) => {
                    item.$checked = val;
                    this.list[index] = item;
                });
            },

            toggleRowSelection(row) {
                let checkedLength = 0;

                this.list.forEach((item, index) => {

                    if(item.$checked) {
                        checkedLength++;
                    }
                    this.list[index] = item;
                });
                if(row.$checked) {
                    if(checkedLength === this.list.length) {
                        this.checkAll = true;
                        this.isIndeterminate = false;
                    }
                } else {
                    if(checkedLength === 0) {
                        this.checkAll = false;
                        this.isIndeterminate = false;
                    } else {
                        if(this.checkAll) {
                            this.isIndeterminate = true;
                        } else {
                            this.checkAll = false;
                        }
                    }
                }
            },

            // check & emit events
            selectDataSet(item, idx) {
                if(this.auditStatus && item.audit_status !== 'agree') {
                    return this.$message({
                        type:                     'error',
                        dangerouslyUseHTMLString: true,
                        message:                  '数据集暂未授权, 无法使用! <div class="mt10"><strong>请先在项目详情中对数据进行授权!</strong></div>',
                    });
                }
                item.$source_page = this.emitEventName;
                if (this.isFlow) this.list[idx] = item;
                this.$emit('selectDataSet', item);
                this.$bus.$emit('selectDataSet', item);
            },

            cancelPopup() {
                this.$emit('close-dialog');
            },

            selectMemberSwitch(item, idx) {
                this.list[idx] = item;
                if (item.$checked) {
                    this.checkedList.push(item);
                } else {
                    this.removeByValue(this.checkedList, 'id', item.id);
                }
            },
            removeByValue(arr, attr, value) {
                let index = 0;

                for(const i in arr){
                    if(arr[i][attr] === value){
                        index = i;
                        break;
                    }
                }
                arr.splice(index, 1);
            },

            addConfirm() {
                // from create project
                if (this.isShowData) {
                    this.batchList = [];
                }
                this.list.forEach(item => {
                    if (item.$checked && !item.$unchanged) {
                        this.batchList.push(item);
                    }
                });
                if(this.batchList.length) {
                    this.$emit('batchDataSet', this.batchList);
                }
                this.$emit('close-dialog');
            },
        },
    };
</script>

<style lang="scss" scoped>
    .data-add{
        width:200px;
        text-align:right;
    }
    .el-alert{
        width: auto;
        height: 30px;
        min-width: 300px;
    }
    .pagination{
        display: flex;
        margin-top: 20px;
    }
    .el-pagination{
        max-width: 90%;
        overflow: auto;
    }
    .btns{
        text-align: right;
        flex: 1;
    }
    .cell-reverse {
        display: flex;
        justify-content: space-around;
        align-items: center;
    }
    .confirm-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        white-space: nowrap;
        padding: 2px 5px;
        p {
            margin-right: 10px;
            span {
                color: #4D84F7;
            }
        }
    }
</style>
