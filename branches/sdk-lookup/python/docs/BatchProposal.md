# BatchProposal

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**gear_id** | **str** |  | [optional] 
**state** | **str** |  | [optional] 
**config** | [**JobConfig**](JobConfig.md) |  | [optional] 
**origin** | [**JobOrigin**](JobOrigin.md) |  | [optional] 
**proposal** | [**BatchProposalDetail**](BatchProposalDetail.md) |  | [optional] 
**ambiguous** | [**list[ContainerOutputWithFiles]**](ContainerOutputWithFiles.md) |  | [optional] 
**matched** | [**list[ContainerOutputWithFiles]**](ContainerOutputWithFiles.md) |  | [optional] 
**not_matched** | [**list[ContainerOutputWithFiles]**](ContainerOutputWithFiles.md) |  | [optional] 
**improper_permissions** | **list[str]** |  | [optional] 
**created** | **datetime** |  | [optional] 
**modified** | **datetime** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


