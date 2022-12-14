<template>
    <el-card
        class="page"
        shadow="never"
    >
        <el-form
            inline
            class="mb20"
            @submit.prevent
        >
            <el-form-item
                label="ID："
                label-width="80"
            >
                <el-input
                    v-model="vData.search.id"
                    clearable
                />
            </el-form-item>
            <el-form-item
                label="名称："
                label-width="80"
            >
                <el-input
                    v-model="vData.search.name"
                    clearable
                />
            </el-form-item>
            <el-form-item
                label="上传者："
                label-width="120"
            >
                <el-select
                    v-model="vData.search.creator"
                    filterable
                    clearable
                >
                    <el-option
                        v-for="(user, index) in vData.userList"
                        :key="index"
                        :label="user.nickname"
                        :value="user.id"
                    />
                </el-select>
            </el-form-item>
            <el-form-item
                label="关键词："
                label-width="100"
            >
                <el-select
                    v-model="vData.search.tag"
                    filterable
                    clearable
                >
                    <el-option
                        v-for="(tag, index) in vData.tagList"
                        :key="index"
                        :value="index"
                    />
                </el-select>
            </el-form-item>
            <el-button
                type="primary"
                native-type="submit"
                @click="searchList({ to: true, resetPagination: true })"
            >
                查询
            </el-button>
        </el-form>

        <el-tabs
            v-model="vData.activeTab"
            type="border-card"
            @tab-click="tabChange"
        >
            <el-tab-pane name="allUnions">
                <template #label>
                    <el-badge>全部数据集</el-badge>
                </template>
                <AllDataList
                    ref="allUnions"
                    key="allUnions"
                    :table-loading="vData.loading"
                    :search-field="vData.search"
                />
            </el-tab-pane>
            <el-tab-pane name="uploadUnions">
                <template #label>
                    <el-badge
                        :max="99"
                        :value="vData.unionTabsCount"
                        :hidden="vData.unionTabsCount < 1"
                        type="danger"
                    >
                        上传中的数据集
                    </el-badge>
                </template>
                <UploadingList
                    ref="uploadUnions"
                    key="uploadUnions"
                    :table-loading="vData.loading"
                    :search-field="vData.search"
                    :upload-list="vData.uploadList"
                />
            </el-tab-pane>
        </el-tabs>
    </el-card>
</template>

<script>
    import {
        ref,
        watch,
        reactive,
        onMounted,
        onBeforeUnmount,
        getCurrentInstance,
    } from 'vue';
    import { useRoute, useRouter } from 'vue-router';
    import UploadingList from './components/uploading-list';
    import AllDataList from './components/all-data-list';

    export default {
        components: {
            AllDataList,
            UploadingList,
        },
        setup() {
            let timer = null;
            const route = useRoute();
            const router = useRouter();
            const { appContext } = getCurrentInstance();
            const { $http, $confirm, $message } = appContext.config.globalProperties;
            const uploadUnions = ref();
            const allUnions = ref();
            const vData = reactive({
                loading: false,
                search:  {
                    id:          '',
                    name:        '',
                    creator:     '',
                    tag:         '',
                    source_type: '',
                },
                userList:       [],
                tagList:        [],
                viewDataDialog: {
                    visible: false,
                    list:    [],
                },
                activeTab:      'allUnions',
                unionTabsCount: 0,
                uploadList:     [], // uploading list
            });
            const methods = {
                async getUploadList() {
                    const $ref = uploadUnions.value;

                    if($ref) {
                        const { code, data } = await $http.get($ref.getListApi, {
                            params: {
                                ...vData.search,
                                page_index: $ref.pagination.page_index - 1,
                                page_size:  $ref.pagination.page_size,
                            },
                        });

                        if (code === 0) {
                            const $data = vData;

                            $data.unionTabsCount = data.total;
                            $data.uploadList = data.list;
                            $ref.pagination.total = data.total;
                            $ref.loading = false;
                        }

                        clearTimeout(timer);
                        timer = setTimeout(() => {
                            methods.getUploadList();
                        }, 2000);

                        if (code === 10006) {
                            clearTimeout(timer);
                        }
                    }
                },

                async getTags() {
                    const { code, data } = await $http.get('/data_set/tags');

                    if (code === 0) {
                        vData.tagList = data;
                    }
                },

                // uploader account list
                async getUploaders() {
                    const { code, data } = await $http.get('/account/query');

                    if (code === 0) {
                        vData.userList = data.list;
                    }
                },

                async deleteData(row) {
                    let message = '此操作将永久删除该条目, 是否继续?';

                    const res = await this.$http.get({
                        url:    '/data_set/usage_detail',
                        params: {
                            dataSetId: row.id,
                        },
                    });

                    if(res.code === 0) {
                        if(res.data && res.data.length) {
                            const list = res.data.map(row => {
                                const path = router.resolve({
                                    name:  'project-detail',
                                    query: {
                                        project_id: row.project_id,
                                    },
                                });

                                return `<a href="${path.href}" target="_blank">${row.name}</a>`;
                            });

                            message = `该数据集在 ${list.join(', ')}, 共 ${res.data.length} 个项目中被使用，`;
                        } else if (row.usage_count_in_project > 0) {
                            message = `该数据集在 ${row.usage_count_in_project} 个项目中被使用，`;
                        }

                        $confirm('警告', {
                            type:                     'warning',
                            dangerouslyUseHTMLString: true,
                            message,
                        }).then(async () => {
                            const { code } = await $http.post({
                                url:  '/data_set/delete',
                                data: {
                                    id: row.id,
                                },
                            });

                            if (code === 0) {
                                $message.success('删除成功!');
                                searchList({ resetPagination: true });
                            }
                        });
                    }
                },
            };
            const tabChange = (refInstance) => {
                router.push({
                    query: {
                        ...vData.search,
                        page_index:  1,
                        source_type: refInstance.paneName,
                    },
                });
                if (refInstance.paneName === 'allUnions') {
                    searchList();
                } else {
                    methods.getUploadList();
                }
            };
            const syncUrlParams = () => {
                vData.search = {
                    id:          '',
                    name:        '',
                    creator:     '',
                    tag:         '',
                    source_type: '',
                    ...route.query,
                };
            };
            const searchList = (opt = {}) => {
                const refInstance = vData.activeTab === 'uploadUnions' ? uploadUnions : allUnions;

                refInstance && refInstance.value.getDataList(opt);
            };

            onMounted(async () => {
                syncUrlParams();
                vData.search.source_type = route.query.source_type || 'allUnions';
                await methods.getTags();
                await methods.getUploaders();
                searchList();
                // Get the list of data sets being uploaded and display corner markers
                await methods.getUploadList();
            });

            onBeforeUnmount(() => {
                clearTimeout(timer);
            });

            watch(
                () => route.query,
                (newVal) => {
                    syncUrlParams();
                    vData.search.source_type = newVal.source_type || 'allUnions';
                    searchList();
                },
                { deep: true },
            );

            return {
                vData,
                searchList,
                syncUrlParams,
                tabChange,
                uploadUnions,
                allUnions,
            };
        },
    };
</script>

<style lang="scss" scoped>
    .el-tabs{
        :deep(.el-tabs__header) {height: 40px;}
        :deep(.el-tabs__nav-wrap){
            overflow: visible;
            margin-bottom:0;
            .el-badge{vertical-align: top;}
        }
        :deep(.el-tabs__nav-scroll){overflow: visible;}
        :deep(.el-tabs__item){
            height: 40px;
            margin-top: 0;
        }
    }
</style>
